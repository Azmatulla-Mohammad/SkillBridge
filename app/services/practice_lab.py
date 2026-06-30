from __future__ import annotations

from dataclasses import dataclass
from html import unescape
import re
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.utils import utcnow
from app.models import PracticeQuestion, PracticeTopic, StudentPracticeProgress, User, UserRole
from app.services.practice_lab_library import build_practice_lab_topics


def _clean_question_description(description: str) -> str:
    cleaned = unescape(description or "")
    cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"</?(?:p|div|span|strong|b|em|i)[^>]*>", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


QUESTION_DESCRIPTION_LABELS = (
    "Topic",
    "Companies Asked",
    "Estimated Interview Frequency",
    "Interview Frequency",
    "Problem Statement",
    "Input Format",
    "Output Format",
    "Constraints",
    "Sample Input",
    "Sample Output",
    "Explanation",
    "Expected Time Complexity",
    "Expected Space Complexity",
)

QUESTION_DESCRIPTION_DISPLAY_LABELS = {
    "Estimated Interview Frequency": "Interview Frequency",
}

QUESTION_CODE_SECTION_LABELS = {"Constraints", "Sample Input", "Sample Output"}
QUESTION_META_SECTION_LABELS = {"Topic", "Companies Asked", "Interview Frequency"}


def _parse_question_description(description: str) -> dict[str, Any]:
    cleaned = _clean_question_description(description)
    label_pattern = "|".join(re.escape(label) for label in QUESTION_DESCRIPTION_LABELS)
    matches = list(re.finditer(rf"(?m)^\s*({label_pattern})\s*:\s*", cleaned))

    if not matches:
        return {
            "summary": cleaned,
            "meta": [],
            "body": [{"label": "Problem Statement", "value": cleaned, "code": False}] if cleaned else [],
        }

    parsed: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        raw_label = match.group(1)
        label = QUESTION_DESCRIPTION_DISPLAY_LABELS.get(raw_label, raw_label)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(cleaned)
        value = cleaned[start:end].strip()
        if not value:
            continue
        parsed.append(
            {
                "label": label,
                "value": value,
                "code": label in QUESTION_CODE_SECTION_LABELS,
            }
        )

    return {
        "summary": "",
        "meta": [section for section in parsed if section["label"] in QUESTION_META_SECTION_LABELS],
        "body": [section for section in parsed if section["label"] not in QUESTION_META_SECTION_LABELS],
    }


DEFAULT_PYTHON_TOPICS: list[dict[str, Any]] = [
    {
        "topic_name": "Python Basics",
        "questions": [
            {
                "title": "Hello World",
                "description": "Write a Python program that prints: Hello World",
                "difficulty": "Easy",
                "starter_code": 'print("Hello World")',
                "expected_output": "Hello World\n",
            },
            {
                "title": "Add Two Numbers",
                "description": "Write a Python program that adds two numbers and prints the result.",
                "difficulty": "Easy",
                "starter_code": "# Write your solution here\n",
            },
            {
                "title": "Even or Odd",
                "description": "Write a Python program that checks whether a number is even or odd.",
                "difficulty": "Easy",
                "starter_code": "# Write your solution here\n",
            },
            {
                "title": "Factorial of a Number",
                "description": "Write a Python program that prints the factorial of a number.",
                "difficulty": "Easy",
                "starter_code": "# Write your solution here\n",
            },
            {
                "title": "Sum of Natural Numbers",
                "description": "Write a Python program that prints the sum of the first n natural numbers.",
                "difficulty": "Easy",
                "starter_code": "# Write your solution here\n",
            },
        ],
    },
    {"topic_name": "Variables", "questions": [{"title": "Variables 101", "description": "Create variables and print them.", "difficulty": "Easy", "starter_code": ""}]},
    {"topic_name": "Data Types", "questions": [{"title": "Identify Types", "description": "Create and print different data types.", "difficulty": "Easy", "starter_code": ""}]},
    {"topic_name": "Operators", "questions": [{"title": "Arithmetic", "description": "Use arithmetic operators to compute and print results.", "difficulty": "Easy", "starter_code": ""}]},
    {"topic_name": "If Statements", "questions": [{"title": "Conditional Output", "description": "Use if statements to print different outputs.", "difficulty": "Easy", "starter_code": ""}]},
    {"topic_name": "Loops", "questions": [{"title": "Looping", "description": "Use loops to iterate and print values.", "difficulty": "Easy", "starter_code": ""}]},
    {"topic_name": "Functions", "questions": [{"title": "Write a Function", "description": "Define and call a function.", "difficulty": "Easy", "starter_code": ""}]},
    {"topic_name": "Lists", "questions": [{"title": "List Operations", "description": "Create a list and access items.", "difficulty": "Easy", "starter_code": ""}]},
    {"topic_name": "Tuples", "questions": [{"title": "Tuple Basics", "description": "Create a tuple and print it.", "difficulty": "Easy", "starter_code": ""}]},
    {"topic_name": "Sets", "questions": [{"title": "Set Uniqueness", "description": "Create a set and show uniqueness.", "difficulty": "Easy", "starter_code": ""}]},
    {"topic_name": "Dictionaries", "questions": [{"title": "Dictionary Lookup", "description": "Create a dictionary and look up a value.", "difficulty": "Easy", "starter_code": ""}]},
    {"topic_name": "Strings", "questions": [{"title": "String Manipulation", "description": "Perform basic string operations.", "difficulty": "Easy", "starter_code": ""}]},
    {"topic_name": "Files", "questions": [{"title": "Read a File", "description": "Demonstrate reading from a file (placeholder).", "difficulty": "Medium", "starter_code": ""}]},
    {"topic_name": "Exception Handling", "questions": [{"title": "Try/Except", "description": "Handle errors using try/except (placeholder).", "difficulty": "Medium", "starter_code": ""}]},
    {"topic_name": "Object-Oriented Programming", "questions": [{"title": "Create a Class", "description": "Create a class and instantiate it (placeholder).", "difficulty": "Medium", "starter_code": ""}]},
]


@dataclass(frozen=True)
class TopicStatistics:
    topic_id: int
    question_count: int
    completion_percentage: int


class PracticeLabService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def ensure_seed_data(self) -> None:
        changed = False
        library_topics = build_practice_lab_topics()
        official_topic_names = {topic["topic_name"] for topic in library_topics}
        official_titles_by_topic = {
            topic["topic_name"]: {question["title"] for question in topic.get("questions", [])}
            for topic in library_topics
        }
        official_question_titles = {
            question["title"]
            for topic in library_topics
            for question in topic.get("questions", [])
        }

        for topic in library_topics:
            topic_obj = self.db.scalar(
                select(PracticeTopic).where(PracticeTopic.topic_name == topic["topic_name"])
            )
            if topic_obj is None:
                topic_obj = PracticeTopic(topic_name=topic["topic_name"])
                self.db.add(topic_obj)
                self.db.flush()
                changed = True

            for q_index, q in enumerate(topic.get("questions", [])):
                question_obj = self.db.scalar(
                    select(PracticeQuestion).where(
                        PracticeQuestion.topic_id == topic_obj.id,
                        PracticeQuestion.title == q["title"],
                    )
                )
                if question_obj is None:
                    question_obj = self.db.scalar(
                        select(PracticeQuestion).where(
                            PracticeQuestion.topic_id == topic_obj.id,
                            PracticeQuestion.display_order == q_index,
                        )
                    )

                if question_obj is None:
                    self.db.add(
                        PracticeQuestion(
                            topic_id=topic_obj.id,
                            title=q["title"],
                            description=q["description"],
                            difficulty=q.get("difficulty", "Easy"),
                            starter_code=q.get("starter_code", ""),
                            expected_output=q.get("expected_output"),
                            display_order=q_index,
                            is_active=True,
                        )
                    )
                    changed = True
                    continue

                updates = {
                    "title": q["title"],
                    "description": q["description"],
                    "difficulty": q.get("difficulty", "Easy"),
                    "starter_code": q.get("starter_code", ""),
                    "expected_output": q.get("expected_output"),
                    "display_order": q_index,
                    "is_active": True,
                }
                for field, value in updates.items():
                    if getattr(question_obj, field) != value:
                        setattr(question_obj, field, value)
                        changed = True

        existing_questions = self.db.execute(
            select(PracticeQuestion, PracticeTopic.topic_name)
            .join(PracticeTopic, PracticeTopic.id == PracticeQuestion.topic_id)
        ).all()
        for question_obj, topic_name in existing_questions:
            is_official = (
                topic_name in official_topic_names
                and question_obj.title in official_titles_by_topic.get(topic_name, set())
                and question_obj.title in official_question_titles
            )
            if not is_official and question_obj.is_active:
                question_obj.is_active = False
                changed = True
            clean_description = _clean_question_description(question_obj.description)
            if question_obj.description != clean_description:
                question_obj.description = clean_description
                changed = True

        if changed:
            self.db.commit()

    def list_questions(self, *, topic_id: int, student_id: int) -> list[dict[str, Any]]:
        self.ensure_seed_data()

        questions = self.db.scalars(
            select(PracticeQuestion)
            .where(
                PracticeQuestion.topic_id == topic_id,
                PracticeQuestion.is_active.is_(True),
            )
            .order_by(PracticeQuestion.display_order.asc(), PracticeQuestion.id.asc())
        ).all()

        if not questions:
            return []

        question_ids = [question.id for question in questions]
        progress = {
            row.question_id: row
            for row in self.db.scalars(
                select(StudentPracticeProgress).where(
                    StudentPracticeProgress.student_id == student_id,
                    StudentPracticeProgress.question_id.in_(question_ids),
                )
            ).all()
        }

        return [
            {
                "id": question.id,
                "title": question.title,
                "description": _clean_question_description(question.description),
                "difficulty": question.difficulty,
                "starter_code": question.starter_code,
                "expected_output": question.expected_output,
                "display_order": question.display_order,
                "completed": bool(progress.get(question.id) and progress[question.id].completed),
                "description_sections": _parse_question_description(question.description),
            }
            for question in questions
        ]

    def list_topics(self, *, student_id: int) -> list[dict[str, Any]]:
        self.ensure_seed_data()

        active_topic_ids = select(PracticeQuestion.topic_id).where(
            PracticeQuestion.is_active.is_(True)
        )
        topics = self.db.scalars(
            select(PracticeTopic)
            .where(PracticeTopic.id.in_(active_topic_ids))
            .order_by(PracticeTopic.id.asc())
        ).all()

        topic_ids = [t.id for t in topics]
        if not topic_ids:
            return []

        # question counts per topic
        q_counts = {
            row._mapping["topic_id"]: row._mapping["question_count"]
            for row in self.db.execute(
                select(
                    PracticeQuestion.topic_id.label("topic_id"),
                    func.count(PracticeQuestion.id).label("question_count"),
                )
                .where(
                    PracticeQuestion.topic_id.in_(topic_ids),
                    PracticeQuestion.is_active.is_(True),
                )
                .group_by(PracticeQuestion.topic_id)
            )
        }


        # completed questions per topic
        completed_counts = {
            row._mapping["topic_id"]: row._mapping["completed_count"]
            for row in self.db.execute(
                select(
                    PracticeQuestion.topic_id.label("topic_id"),
                    func.count(StudentPracticeProgress.question_id).label("completed_count"),
                )
                .join(PracticeQuestion, PracticeQuestion.id == StudentPracticeProgress.question_id)
                .where(
                    StudentPracticeProgress.student_id == student_id,
                    StudentPracticeProgress.completed.is_(True),
                    PracticeQuestion.topic_id.in_(topic_ids),
                    PracticeQuestion.is_active.is_(True),
                )
                .group_by(PracticeQuestion.topic_id)
            )
        }

        result: list[dict[str, Any]] = []
        for topic in topics:
            total = int(q_counts.get(topic.id, 0) or 0)
            completed = int(completed_counts.get(topic.id, 0) or 0)
            completion_percentage = int((completed / total) * 100) if total > 0 else 0

            result.append(
                {
                    "id": topic.id,
                    "topic_name": topic.topic_name,
                    "question_count": total,
                    "completion_percentage": completion_percentage,
                }
            )

        return result

    def get_topic(self, topic_id: int) -> PracticeTopic | None:
        self.ensure_seed_data()
        return self.db.scalar(select(PracticeTopic).where(PracticeTopic.id == topic_id))

    def get_first_question(self, *, topic_id: int) -> PracticeQuestion | None:
        self.ensure_seed_data()
        return self.db.scalar(
            select(PracticeQuestion)
            .where(
                PracticeQuestion.topic_id == topic_id,
                PracticeQuestion.is_active.is_(True),
            )
            .order_by(PracticeQuestion.display_order.asc(), PracticeQuestion.id.asc())
            .limit(1)
        )

