from __future__ import annotations

from app.models import ActivityLog, Announcement, Assignment, Course, Enrollment, Material, Meeting, Submission, User


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role.value,
        "phone": user.phone,
        "bio": user.bio,
        "is_active": user.is_active,
        "headline": user.teacher_profile.headline if user.teacher_profile else None,
        "expertise": user.teacher_profile.expertise if user.teacher_profile else None,
        "meeting_link": user.teacher_profile.meeting_link if user.teacher_profile else None,
        "guardian_name": user.student_profile.guardian_name if user.student_profile else None,
        "learning_goals": user.student_profile.learning_goals if user.student_profile else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def course_to_dict(course: Course) -> dict:
    return {
        "id": course.id,
        "title": course.title,
        "slug": course.slug,
        "description": course.description,
        "duration_weeks": course.duration_weeks,
        "price": course.price,
        "is_active": course.is_active,
        "created_at": course.created_at.isoformat() if course.created_at else None,
    }


def enrollment_to_dict(enrollment: Enrollment) -> dict:
    return {
        "id": enrollment.id,
        "status": enrollment.status.value,
        "start_date": enrollment.start_date.isoformat() if enrollment.start_date else None,
        "progress_percent": enrollment.progress_percent,
        "meeting_link": enrollment.meeting_link,
        "notes": enrollment.notes,
        "student": {
            "id": enrollment.student.id,
            "full_name": enrollment.student.full_name,
            "email": enrollment.student.email,
        },
        "teacher": {
            "id": enrollment.teacher.id,
            "full_name": enrollment.teacher.full_name,
            "email": enrollment.teacher.email,
        },
        "course": course_to_dict(enrollment.course),
    }


def material_to_dict(material: Material) -> dict:
    return {
        "id": material.id,
        "title": material.title,
        "description": material.description,
        "file_url": material.file_url,
        "original_filename": material.original_filename,
        "content_type": material.content_type,
        "course": course_to_dict(material.course),
        "teacher": {"id": material.teacher.id, "full_name": material.teacher.full_name},
        "created_at": material.created_at.isoformat() if material.created_at else None,
    }


def assignment_to_dict(assignment: Assignment) -> dict:
    return {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "due_at": assignment.due_at.isoformat() if assignment.due_at else None,
        "max_score": assignment.max_score,
        "attachment_url": assignment.attachment_url,
        "course": course_to_dict(assignment.course),
        "teacher": {"id": assignment.teacher.id, "full_name": assignment.teacher.full_name},
        "created_at": assignment.created_at.isoformat() if assignment.created_at else None,
    }


def submission_to_dict(submission: Submission) -> dict:
    return {
        "id": submission.id,
        "file_url": submission.file_url,
        "original_filename": submission.original_filename,
        "content_type": submission.content_type,
        "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
        "score": submission.score,
        "feedback": submission.feedback,
        "reviewed_at": submission.reviewed_at.isoformat() if submission.reviewed_at else None,
        "student": {"id": submission.student.id, "full_name": submission.student.full_name},
        "assignment": assignment_to_dict(submission.assignment),
    }


def announcement_to_dict(announcement: Announcement) -> dict:
    return {
        "id": announcement.id,
        "title": announcement.title,
        "content": announcement.content,
        "course": course_to_dict(announcement.course),
        "teacher": {"id": announcement.teacher.id, "full_name": announcement.teacher.full_name},
        "created_at": announcement.created_at.isoformat() if announcement.created_at else None,
    }


def meeting_to_dict(meeting: Meeting) -> dict:
    return {
        "id": meeting.id,
        "title": meeting.title,
        "meeting_url": meeting.meeting_url,
        "scheduled_at": meeting.scheduled_at.isoformat() if meeting.scheduled_at else None,
        "notes": meeting.notes,
        "teacher": {"id": meeting.teacher.id, "full_name": meeting.teacher.full_name},
        "student": {
            "id": meeting.enrollment.student.id,
            "full_name": meeting.enrollment.student.full_name,
        },
        "course": course_to_dict(meeting.enrollment.course),
    }


def activity_to_dict(activity: ActivityLog) -> dict:
    return {
        "id": activity.id,
        "action": activity.action,
        "entity_type": activity.entity_type,
        "entity_id": activity.entity_id,
        "summary": activity.summary,
        "metadata": activity.metadata_json,
        "created_at": activity.created_at.isoformat() if activity.created_at else None,
        "actor": (
            {"id": activity.actor.id, "full_name": activity.actor.full_name}
            if activity.actor
            else None
        ),
    }

