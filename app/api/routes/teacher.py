from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import require_api_user
from app.api.serializers import (
    announcement_to_dict,
    assignment_to_dict,
    enrollment_to_dict,
    material_to_dict,
    meeting_to_dict,
    submission_to_dict,
    user_to_dict,
)
from app.core.database import get_db
from app.models import UserRole
from app.schemas.teacher import (
    AnnouncementCreate,
    MeetingCreate,
    SubmissionReview,
    TeacherAssignmentCreate,
    TeacherAssignmentUpdate,
    TeacherMaterialCreate,
    TeacherProfileUpdate,
)
from app.services.teacher import TeacherService


router = APIRouter(prefix="/teacher", tags=["api-teacher"])


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    context = TeacherService(db).dashboard(current_user.id)
    return {
        "student_count": context["student_count"],
        "assignment_count": context["assignment_count"],
        "material_count": context["material_count"],
        "enrollments": [enrollment_to_dict(item) for item in context["enrollments"]],
        "recent_submissions": [submission_to_dict(item) for item in context["recent_submissions"]],
        "upcoming_meetings": [meeting_to_dict(item) for item in context["upcoming_meetings"]],
    }


@router.get("/students")
def students(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    enrollments, total = TeacherService(db).list_students(current_user.id, search=search, page=page, page_size=20)
    return {"items": [user_to_dict(item.student) for item in enrollments], "total": total}


@router.get("/materials")
def materials(
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    items, total = TeacherService(db).list_materials(current_user.id, page=page, page_size=20)
    return {"items": [material_to_dict(item) for item in items], "total": total}


@router.post("/materials")
async def create_material(
    title: str = Form(...),
    description: str = Form(default=""),
    course_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    material = await TeacherService(db).create_material(
        current_user.id,
        TeacherMaterialCreate(title=title, description=description or None, course_id=course_id),
        file,
    )
    return material_to_dict(material)


@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    await TeacherService(db).delete_material(current_user.id, material_id)
    return {"success": True}


@router.get("/assignments")
def assignments(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    items, total = TeacherService(db).list_assignments(current_user.id, search=search, page=page, page_size=20)
    return {"items": [assignment_to_dict(item) for item in items], "total": total}


@router.post("/assignments")
async def create_assignment(
    title: str = Form(...),
    description: str = Form(...),
    course_id: int = Form(...),
    due_at: str | None = Form(default=None),
    max_score: int = Form(default=100),
    attachment: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    assignment = await TeacherService(db).create_assignment(
        current_user.id,
        TeacherAssignmentCreate(
            title=title,
            description=description,
            course_id=course_id,
            due_at=due_at,
            max_score=max_score,
        ),
        upload=attachment,
    )
    return assignment_to_dict(assignment)


@router.put("/assignments/{assignment_id}")
async def update_assignment(
    assignment_id: int,
    payload: TeacherAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    updated = await TeacherService(db).update_assignment(
        current_user.id,
        assignment_id,
        payload,
        upload=None,
    )
    return assignment_to_dict(updated)


@router.delete("/assignments/{assignment_id}")
async def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    await TeacherService(db).delete_assignment(current_user.id, assignment_id)
    return {"success": True}


@router.get("/submissions")
def submissions(
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    items, total = TeacherService(db).list_submissions(current_user.id, page=page, page_size=20)
    return {"items": [submission_to_dict(item) for item in items], "total": total}


@router.post("/submissions/{submission_id}/feedback")
def review_submission(
    submission_id: int,
    payload: SubmissionReview,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    submission = TeacherService(db).review_submission(current_user.id, submission_id, payload)
    return submission_to_dict(submission)


@router.get("/announcements")
def announcements(
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    items, total = TeacherService(db).list_announcements(current_user.id, page=page, page_size=20)
    return {"items": [announcement_to_dict(item) for item in items], "total": total}


@router.post("/announcements")
def create_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    return announcement_to_dict(TeacherService(db).create_announcement(current_user.id, payload))


@router.delete("/announcements/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    TeacherService(db).delete_announcement(current_user.id, announcement_id)
    return {"success": True}


@router.get("/meetings")
def meetings(
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    items, total = TeacherService(db).list_meetings(current_user.id, page=page, page_size=20)
    return {"items": [meeting_to_dict(item) for item in items], "total": total}


@router.post("/meetings")
def create_meeting(
    payload: MeetingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    return meeting_to_dict(TeacherService(db).create_meeting(current_user.id, payload))


@router.delete("/meetings/{meeting_id}")
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    TeacherService(db).delete_meeting(current_user.id, meeting_id)
    return {"success": True}


@router.get("/profile")
def profile(
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    return user_to_dict(TeacherService(db).user_repo.get(current_user.id))


@router.put("/profile")
def update_profile(
    payload: TeacherProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.TEACHER)),
):
    return user_to_dict(TeacherService(db).update_profile(current_user.id, payload))
