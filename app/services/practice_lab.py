from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.utils import utcnow
from app.models import PracticeQuestion, PracticeTopic, StudentPracticeProgress, User, UserRole


DEFAULT_PYTHON_TOPICS: list[dict[str, Any]] = [
    {"topic_name": "Python Basics", "questions": [{"title": "Print Hello World", "description": "Write a Python program that prints:\n\nHello World", "difficulty": "Easy", "starter_code": ""}]},
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
        existing_count = self.db.scalar(select(func.count(PracticeTopic.id))) or 0
        if existing_count > 0:
            return

        for topic_index, topic in enumerate(DEFAULT_PYTHON_TOPICS):
            topic_obj = PracticeTopic(topic_name=topic["topic_name"])
            self.db.add(topic_obj)
            self.db.flush()  # assign id

            for q_index, q in enumerate(topic.get("questions", [])):
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

        self.db.commit()

    def list_topics(self, *, student_id: int) -> list[dict[str, Any]]:
        self.ensure_seed_data()

        topics = self.db.scalars(select(PracticeTopic).order_by(PracticeTopic.id.asc())).all()

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
                .where(PracticeQuestion.topic_id.in_(topic_ids))
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

