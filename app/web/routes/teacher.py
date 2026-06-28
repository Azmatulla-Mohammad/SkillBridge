from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from sqlalchemy.orm import Session

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
from app.web.dependencies import (
    pagination,
    parse_datetime_input,
    redirect_with_flash,
    render_template,
    require_web_user,
    validate_csrf,
)


router = APIRouter(prefix="/teacher", tags=["web-teacher"])


@router.get("", name="teacher_dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    context = TeacherService(db).dashboard(current_user.id)
    return render_template(
        request,
        "teacher/dashboard.html",
        title="Teacher Dashboard",
        current_user=current_user,
        **context,
    )


@router.get("/students", name="teacher_students")
def students_page(
    request: Request,
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    enrollments, total = TeacherService(db).list_students(
        current_user.id,
        search=search,
        page=page,
        page_size=10,
    )
    return render_template(
        request,
        "teacher/students.html",
        title="My Students",
        current_user=current_user,
        enrollments=enrollments,
        total=total,
        pager=pagination(page, 10, total),
        search=search or "",
    )


@router.get("/materials", name="teacher_materials")
def materials_page(
    request: Request,
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    service = TeacherService(db)
    materials, total = service.list_materials(current_user.id, page=page, page_size=10)
    return render_template(
        request,
        "teacher/materials.html",
        title="Study Materials",
        current_user=current_user,
        materials=materials,
        total=total,
        pager=pagination(page, 10, total),
        courses=[course for course in service.course_options(current_user.id) if course],
    )


@router.post("/materials", name="teacher_materials_create")
async def create_material(
    request: Request,
    csrf_token: str = Form(...),
    title: str = Form(...),
    description: str = Form(default=""),
    course_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    try:
        validate_csrf(request, csrf_token)
        await TeacherService(db).create_material(
            current_user.id,
            TeacherMaterialCreate(title=title, description=description or None, course_id=course_id),
            file,
        )
        return redirect_with_flash(request, "/teacher/materials", message="Material uploaded successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/teacher/materials", message=str(exc), level="error")


@router.post("/materials/{material_id}/delete", name="teacher_materials_delete")
async def delete_material(
    material_id: int,
    request: Request,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    try:
        validate_csrf(request, csrf_token)
        await TeacherService(db).delete_material(current_user.id, material_id)
        return redirect_with_flash(request, "/teacher/materials", message="Material deleted successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/teacher/materials", message=str(exc), level="error")


@router.get("/assignments", name="teacher_assignments")
def assignments_page(
    request: Request,
    search: str | None = Query(default=None),
    edit: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    service = TeacherService(db)
    assignments, total = service.list_assignments(current_user.id, search=search, page=page, page_size=10)
    submissions, _ = service.list_submissions(current_user.id, page=1, page_size=5)
    return render_template(
        request,
        "teacher/assignments.html",
        title="Assignments",
        current_user=current_user,
        assignments=assignments,
        total=total,
        pager=pagination(page, 10, total),
        edit_assignment=service.academic_repo.get_assignment(edit) if edit else None,
        courses=[course for course in service.course_options(current_user.id) if course],
        submissions=submissions,
        search=search or "",
    )


@router.post("/assignments", name="teacher_assignments_create")
async def create_assignment(
    request: Request,
    csrf_token: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    course_id: int = Form(...),
    due_at: str = Form(default=""),
    max_score: int = Form(default=100),
    attachment: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    try:
        validate_csrf(request, csrf_token)
        await TeacherService(db).create_assignment(
            current_user.id,
            TeacherAssignmentCreate(
                title=title,
                description=description,
                course_id=course_id,
                due_at=parse_datetime_input(due_at),
                max_score=max_score,
            ),
            upload=attachment,
        )
        return redirect_with_flash(request, "/teacher/assignments", message="Assignment created successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/teacher/assignments", message=str(exc), level="error")


@router.post("/assignments/{assignment_id}/update", name="teacher_assignments_update")
async def update_assignment(
    assignment_id: int,
    request: Request,
    csrf_token: str = Form(...),
    title: str = Form(default=""),
    description: str = Form(default=""),
    due_at: str = Form(default=""),
    max_score: int = Form(default=100),
    attachment: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    try:
        validate_csrf(request, csrf_token)
        await TeacherService(db).update_assignment(
            current_user.id,
            assignment_id,
            TeacherAssignmentUpdate(
                title=title or None,
                description=description or None,
                due_at=parse_datetime_input(due_at),
                max_score=max_score,
            ),
            upload=attachment,
        )
        return redirect_with_flash(request, "/teacher/assignments", message="Assignment updated successfully.")
    except Exception as exc:
        return redirect_with_flash(
            request,
            f"/teacher/assignments?edit={assignment_id}",
            message=str(exc),
            level="error",
        )


@router.post("/assignments/{assignment_id}/delete", name="teacher_assignments_delete")
async def delete_assignment(
    assignment_id: int,
    request: Request,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    try:
        validate_csrf(request, csrf_token)
        await TeacherService(db).delete_assignment(current_user.id, assignment_id)
        return redirect_with_flash(request, "/teacher/assignments", message="Assignment deleted successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/teacher/assignments", message=str(exc), level="error")


@router.get("/submissions/{submission_id}", name="teacher_submission_review")
def review_submission_page(
    submission_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    submission = TeacherService(db).academic_repo.get_submission(submission_id)
    if not submission or submission.assignment.teacher_id != current_user.id:
        return redirect_with_flash(request, "/teacher/assignments", message="Submission not found.", level="error")
    return render_template(
        request,
        "teacher/submission_review.html",
        title="Review Submission",
        current_user=current_user,
        submission=submission,
    )


@router.post("/submissions/{submission_id}/review", name="teacher_submission_review_submit")
def review_submission(
    submission_id: int,
    request: Request,
    csrf_token: str = Form(...),
    score: int = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    try:
        validate_csrf(request, csrf_token)
        TeacherService(db).review_submission(
            current_user.id,
            submission_id,
            SubmissionReview(score=score, feedback=feedback),
        )
        return redirect_with_flash(request, "/teacher/assignments", message="Feedback saved successfully.")
    except Exception as exc:
        return redirect_with_flash(
            request,
            f"/teacher/submissions/{submission_id}",
            message=str(exc),
            level="error",
        )


@router.get("/announcements", name="teacher_announcements")
def announcements_page(
    request: Request,
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    service = TeacherService(db)
    announcements, total = service.list_announcements(current_user.id, page=page, page_size=10)
    return render_template(
        request,
        "teacher/announcements.html",
        title="Announcements",
        current_user=current_user,
        announcements=announcements,
        total=total,
        pager=pagination(page, 10, total),
        courses=[course for course in service.course_options(current_user.id) if course],
    )


@router.post("/announcements", name="teacher_announcements_create")
def create_announcement(
    request: Request,
    csrf_token: str = Form(...),
    course_id: int = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    try:
        validate_csrf(request, csrf_token)
        TeacherService(db).create_announcement(
            current_user.id,
            AnnouncementCreate(course_id=course_id, title=title, content=content),
        )
        return redirect_with_flash(request, "/teacher/announcements", message="Announcement published successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/teacher/announcements", message=str(exc), level="error")


@router.post("/announcements/{announcement_id}/delete", name="teacher_announcements_delete")
def delete_announcement(
    announcement_id: int,
    request: Request,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    try:
        validate_csrf(request, csrf_token)
        TeacherService(db).delete_announcement(current_user.id, announcement_id)
        return redirect_with_flash(request, "/teacher/announcements", message="Announcement deleted successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/teacher/announcements", message=str(exc), level="error")


@router.get("/meetings", name="teacher_meetings")
def meetings_page(
    request: Request,
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    service = TeacherService(db)
    meetings, total = service.list_meetings(current_user.id, page=page, page_size=10)
    enrollments, _ = service.list_students(current_user.id, search=None, page=1, page_size=200)
    return render_template(
        request,
        "teacher/meetings.html",
        title="Meetings",
        current_user=current_user,
        meetings=meetings,
        total=total,
        pager=pagination(page, 10, total),
        enrollments=enrollments,
    )


@router.post("/meetings", name="teacher_meetings_create")
def create_meeting(
    request: Request,
    csrf_token: str = Form(...),
    enrollment_id: int = Form(...),
    title: str = Form(...),
    meeting_url: str = Form(...),
    scheduled_at: str = Form(...),
    notes: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    try:
        validate_csrf(request, csrf_token)
        TeacherService(db).create_meeting(
            current_user.id,
            MeetingCreate(
                enrollment_id=enrollment_id,
                title=title,
                meeting_url=meeting_url,
                scheduled_at=parse_datetime_input(scheduled_at),
                notes=notes or None,
            ),
        )
        return redirect_with_flash(request, "/teacher/meetings", message="Meeting scheduled successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/teacher/meetings", message=str(exc), level="error")


@router.post("/meetings/{meeting_id}/delete", name="teacher_meetings_delete")
def delete_meeting(
    meeting_id: int,
    request: Request,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    try:
        validate_csrf(request, csrf_token)
        TeacherService(db).delete_meeting(current_user.id, meeting_id)
        return redirect_with_flash(request, "/teacher/meetings", message="Meeting deleted successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/teacher/meetings", message=str(exc), level="error")


@router.get("/profile", name="teacher_profile")
def profile_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    user = TeacherService(db).user_repo.get(current_user.id)
    return render_template(
        request,
        "teacher/profile.html",
        title="Teacher Profile",
        current_user=current_user,
        profile_user=user,
    )


@router.post("/profile", name="teacher_profile_update")
def update_profile(
    request: Request,
    csrf_token: str = Form(...),
    full_name: str = Form(default=""),
    phone: str = Form(default=""),
    bio: str = Form(default=""),
    headline: str = Form(default=""),
    expertise: str = Form(default=""),
    meeting_link: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.TEACHER)),
):
    try:
        validate_csrf(request, csrf_token)
        TeacherService(db).update_profile(
            current_user.id,
            TeacherProfileUpdate(
                full_name=full_name or None,
                phone=phone or None,
                bio=bio or None,
                headline=headline or None,
                expertise=expertise or None,
                meeting_link=meeting_link or None,
            ),
        )
        return redirect_with_flash(request, "/teacher/profile", message="Profile updated successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/teacher/profile", message=str(exc), level="error")

