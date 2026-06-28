from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import require_api_user
from app.api.serializers import (
    activity_to_dict,
    assignment_to_dict,
    course_to_dict,
    enrollment_to_dict,
    meeting_to_dict,
    user_to_dict,
)
from app.core.database import get_db
from app.core.storage import SupabaseStorageService
from app.models import UserRole
from app.schemas.admin import (
    AssignmentAdminCreate,
    AssignmentAdminUpdate,
    CourseCreate,
    CourseUpdate,
    EnrollmentCreate,
    EnrollmentUpdate,
    UserCreate,
    UserUpdate,
)
from app.services.admin import AdminService


router = APIRouter(prefix="/admin", tags=["api-admin"])


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    context = AdminService(db).dashboard()
    return {
        "stats": context["stats"],
        "recent_activity": [activity_to_dict(item) for item in context["recent_activity"]],
        "upcoming_meetings": [meeting_to_dict(item) for item in context["upcoming_meetings"]],
    }


@router.get("/teachers")
def list_teachers(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    users, total = AdminService(db).list_users(role=UserRole.TEACHER, search=search, is_active=None, page=page, page_size=20)
    return {"items": [user_to_dict(item) for item in users], "total": total}


@router.post("/teachers")
def create_teacher(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    payload.role = UserRole.TEACHER
    return user_to_dict(AdminService(db).create_user(payload, actor_id=current_user.id))


@router.put("/teachers/{user_id}")
def update_teacher(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    return user_to_dict(AdminService(db).update_user(user_id, payload, actor_id=current_user.id))


@router.delete("/teachers/{user_id}")
def delete_teacher(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    AdminService(db).delete_user(user_id, actor_id=current_user.id)
    return {"success": True}


@router.get("/students")
def list_students(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    users, total = AdminService(db).list_users(role=UserRole.STUDENT, search=search, is_active=None, page=page, page_size=20)
    return {"items": [user_to_dict(item) for item in users], "total": total}


@router.post("/students")
def create_student(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    payload.role = UserRole.STUDENT
    return user_to_dict(AdminService(db).create_user(payload, actor_id=current_user.id))


@router.put("/students/{user_id}")
def update_student(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    return user_to_dict(AdminService(db).update_user(user_id, payload, actor_id=current_user.id))


@router.delete("/students/{user_id}")
def delete_student(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    AdminService(db).delete_user(user_id, actor_id=current_user.id)
    return {"success": True}


@router.post("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    return user_to_dict(AdminService(db).set_user_active_state(user_id, True, actor_id=current_user.id))


@router.post("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    return user_to_dict(AdminService(db).set_user_active_state(user_id, False, actor_id=current_user.id))


@router.post("/users/{user_id}/reset-password")
def reset_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    password = AdminService(db).reset_password(user_id, actor_id=current_user.id)
    return {"temporary_password": password}


@router.get("/courses")
def list_courses(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    courses, total = AdminService(db).list_courses(search=search, is_active=None, page=page, page_size=20)
    return {"items": [course_to_dict(item) for item in courses], "total": total}


@router.post("/courses")
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    return course_to_dict(AdminService(db).create_course(payload, actor_id=current_user.id))


@router.put("/courses/{course_id}")
def update_course(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    return course_to_dict(AdminService(db).update_course(course_id, payload, actor_id=current_user.id))


@router.delete("/courses/{course_id}")
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    AdminService(db).delete_course(course_id, actor_id=current_user.id)
    return {"success": True}


@router.get("/enrollments")
def list_enrollments(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    items, total = AdminService(db).list_enrollments(search=search, teacher_id=None, student_id=None, course_id=None, page=page, page_size=20)
    return {"items": [enrollment_to_dict(item) for item in items], "total": total}


@router.post("/enrollments")
def create_enrollment(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    return enrollment_to_dict(AdminService(db).create_enrollment(payload, actor_id=current_user.id))


@router.put("/enrollments/{enrollment_id}")
def update_enrollment(
    enrollment_id: int,
    payload: EnrollmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    return enrollment_to_dict(AdminService(db).update_enrollment(enrollment_id, payload, actor_id=current_user.id))


@router.delete("/enrollments/{enrollment_id}")
def delete_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    AdminService(db).delete_enrollment(enrollment_id, actor_id=current_user.id)
    return {"success": True}


@router.get("/assignments")
def list_assignments(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    items, total = AdminService(db).list_assignments(search=search, course_id=None, teacher_id=None, page=page, page_size=20)
    return {"items": [assignment_to_dict(item) for item in items], "total": total}


@router.post("/assignments")
async def create_assignment(
    title: str = Form(...),
    description: str = Form(...),
    course_id: int = Form(...),
    teacher_id: int = Form(...),
    due_at: str | None = Form(default=None),
    max_score: int = Form(default=100),
    attachment: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    attachment_url = None
    if attachment and attachment.filename:
        attachment_url = (await SupabaseStorageService().upload_file(attachment, "admin-assignments", owner_id=current_user.id)).file_url
    payload = AssignmentAdminCreate(
        title=title,
        description=description,
        course_id=course_id,
        teacher_id=teacher_id,
        due_at=due_at,
        max_score=max_score,
        attachment_url=attachment_url,
    )
    return assignment_to_dict(AdminService(db).create_assignment(payload, actor_id=current_user.id))


@router.put("/assignments/{assignment_id}")
def update_assignment(
    assignment_id: int,
    payload: AssignmentAdminUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    return assignment_to_dict(AdminService(db).update_assignment(assignment_id, payload, actor_id=current_user.id))


@router.delete("/assignments/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    AdminService(db).delete_assignment(assignment_id, actor_id=current_user.id)
    return {"success": True}


@router.get("/logs")
def activity_logs(
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_api_user(UserRole.ADMIN)),
):
    logs, total = AdminService(db).list_logs(search=search, page=page, page_size=50)
    return {"items": [activity_to_dict(item) for item in logs], "total": total}
