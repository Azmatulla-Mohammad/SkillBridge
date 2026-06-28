from fastapi import APIRouter, Depends, File, Query, UploadFile
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
from app.schemas.student import StudentProfileUpdate
from app.services.student import StudentService


router = APIRouter(prefix="/student", tags=["api-student"])


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.STUDENT)),
):
    context = StudentService(db).dashboard(current_user.id)
    return {
        "enrollments": [enrollment_to_dict(item) for item in context["enrollments"]],
        "assignments": [assignment_to_dict(item) for item in context["assignments"]],
        "materials": [material_to_dict(item) for item in context["materials"]],
        "announcements": [announcement_to_dict(item) for item in context["announcements"]],
        "meetings": [meeting_to_dict(item) for item in context["meetings"]],
        "submissions": [submission_to_dict(item) for item in context["submissions"]],
    }


@router.get("/course")
def course(
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.STUDENT)),
):
    return [
        enrollment_to_dict(item)
        for item in StudentService(db).dashboard(current_user.id)["enrollments"]
    ]


@router.get("/materials")
def materials(
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.STUDENT)),
):
    items, total = StudentService(db).list_materials(current_user.id, page=page, page_size=20)
    return {"items": [material_to_dict(item) for item in items], "total": total}


@router.get("/assignments")
def assignments(
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.STUDENT)),
):
    items, total = StudentService(db).list_assignments(current_user.id, page=page, page_size=20)
    return {"items": [assignment_to_dict(item) for item in items], "total": total}


@router.post("/assignments/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.STUDENT)),
):
    return submission_to_dict(await StudentService(db).submit_assignment(current_user.id, assignment_id, file))


@router.get("/submissions")
def feedback(
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.STUDENT)),
):
    items, total = StudentService(db).list_feedback(current_user.id, page=page, page_size=20)
    return {"items": [submission_to_dict(item) for item in items], "total": total}


@router.get("/meetings")
def meetings(
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.STUDENT)),
):
    items, total = StudentService(db).list_meetings(current_user.id, page=page, page_size=20)
    return {"items": [meeting_to_dict(item) for item in items], "total": total}


@router.get("/announcements")
def announcements(
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.STUDENT)),
):
    items, total = StudentService(db).list_announcements(current_user.id, page=page, page_size=20)
    return {"items": [announcement_to_dict(item) for item in items], "total": total}


@router.get("/profile")
def profile(
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.STUDENT)),
):
    return user_to_dict(StudentService(db).user_repo.get(current_user.id))


@router.put("/profile")
def update_profile(
    payload: StudentProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.STUDENT)),
):
    return user_to_dict(StudentService(db).update_profile(current_user.id, payload))
