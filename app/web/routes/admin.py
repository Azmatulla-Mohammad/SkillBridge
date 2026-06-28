from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from sqlalchemy.orm import Session

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
from app.web.dependencies import (
    pagination,
    parse_date_input,
    parse_datetime_input,
    redirect_with_flash,
    render_template,
    require_web_user,
    validate_csrf,
)


router = APIRouter(prefix="/admin", tags=["web-admin"])


def _parse_active_filter(value: str | None):
    if value == "active":
        return True
    if value == "inactive":
        return False
    return None


@router.get("", name="admin_dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    context = AdminService(db).dashboard()
    return render_template(request, "admin/dashboard.html", title="Admin Dashboard", current_user=current_user, **context)


@router.get("/users", name="admin_users")
def users_page(
    request: Request,
    role: str | None = Query(default=None),
    active: str | None = Query(default=None),
    search: str | None = Query(default=None),
    edit: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    service = AdminService(db)
    role_enum = UserRole(role) if role else None
    active_filter = _parse_active_filter(active)
    users, total = service.list_users(
        role=role_enum,
        search=search,
        is_active=active_filter,
        page=page,
        page_size=10,
    )
    edit_user = service.user_repo.get(edit) if edit else None
    return render_template(
        request,
        "admin/users.html",
        title="Manage Users",
        current_user=current_user,
        users=users,
        total=total,
        pager=pagination(page, 10, total),
        edit_user=edit_user,
        role_filter=role or "",
        active_filter=active or "",
        search=search or "",
        role_counts=service.user_repo.role_counts(),
    )


@router.post("/users", name="admin_users_create")
def create_user(
    request: Request,
    csrf_token: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(default=""),
    role: str = Form(...),

    phone: str = Form(default=""),
    bio: str = Form(default=""),
    headline: str = Form(default=""),
    expertise: str = Form(default=""),
    guardian_name: str = Form(default=""),
    learning_goals: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        created_user, temporary_password = AdminService(db).create_user(
            UserCreate(
                full_name=full_name,
                email=email,
                password=password.strip(),
                role=UserRole(role),
                phone=phone or None,
                bio=bio or None,
                headline=headline or None,
                expertise=expertise or None,
                guardian_name=guardian_name or None,
                learning_goals=learning_goals or None,
            ),
            actor_id=current_user.id,
        )
        if temporary_password:
            # One-time response render (no flash / no URL params / no persistent storage).
            service = AdminService(db)
            users, total = service.list_users(
                role=UserRole(role),
                search=None,
                is_active=None,
                page=1,
                page_size=10,
            )
            return render_template(
                request,
                "admin/users.html",
                title="Manage Users",
                current_user=current_user,
                users=users,
                total=total,
                pager=pagination(1, 10, total),
                edit_user=None,
                role_filter=role,
                active_filter="",
                search="",
                role_counts=service.user_repo.role_counts(),
                modal_created_user={
                    "email": created_user.email,
                    "temporary_password": temporary_password,
                    "role": created_user.role.value,
                },
                modal_shown=True,

            )

        return redirect_with_flash(request, "/admin/users", message="User created successfully.")


    except Exception as exc:
        return redirect_with_flash(request, "/admin/users", message=str(exc), level="error")


@router.post("/users/{user_id}/update", name="admin_users_update")
def update_user(
    user_id: int,
    request: Request,
    csrf_token: str = Form(...),
    full_name: str = Form(default=""),
    email: str = Form(default=""),
    password: str = Form(default=""),
    phone: str = Form(default=""),
    bio: str = Form(default=""),
    headline: str = Form(default=""),
    expertise: str = Form(default=""),
    guardian_name: str = Form(default=""),
    learning_goals: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        AdminService(db).update_user(
            user_id,
            UserUpdate(
                full_name=full_name or None,
                email=email or None,
                password=password or None,
                phone=phone or None,
                bio=bio or None,
                headline=headline or None,
                expertise=expertise or None,
                guardian_name=guardian_name or None,
                learning_goals=learning_goals or None,
            ),
            actor_id=current_user.id,
        )
        return redirect_with_flash(request, "/admin/users", message="User updated successfully.")
    except Exception as exc:
        return redirect_with_flash(request, f"/admin/users?edit={user_id}", message=str(exc), level="error")


@router.post("/users/{user_id}/toggle", name="admin_users_toggle")
def toggle_user(
    user_id: int,
    request: Request,
    csrf_token: str = Form(...),
    state: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        is_active = state == "active"
        AdminService(db).set_user_active_state(user_id, is_active=is_active, actor_id=current_user.id)
        return redirect_with_flash(
            request,
            "/admin/users",
            message=f"User {'activated' if is_active else 'deactivated'} successfully.",
        )
    except Exception as exc:
        return redirect_with_flash(request, "/admin/users", message=str(exc), level="error")


@router.post("/users/{user_id}/reset-password", name="admin_users_reset_password")
def reset_password(
    user_id: int,
    request: Request,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        temporary_password = AdminService(db).reset_password(user_id, actor_id=current_user.id)
        reset_user = AdminService(db).user_repo.get(user_id)
        service = AdminService(db)
        users, total = service.list_users(role=None, search=None, is_active=None, page=1, page_size=10)
        return render_template(
            request,
            "admin/users.html",
            title="Manage Users",
            current_user=current_user,
            users=users,
            total=total,
            pager=pagination(1, 10, total),
            edit_user=None,
            role_filter="",
            active_filter="",
            search="",
            role_counts=service.user_repo.role_counts(),
            modal_created_user={
                "email": reset_user.email if reset_user else "",
                "temporary_password": temporary_password,
                "role": reset_user.role.value if reset_user else "",
            },
        )

    except Exception as exc:
        return redirect_with_flash(request, "/admin/users", message=str(exc), level="error")


@router.post("/users/{user_id}/delete", name="admin_users_delete")
def delete_user(
    user_id: int,
    request: Request,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        AdminService(db).delete_user(user_id, actor_id=current_user.id)
        return redirect_with_flash(request, "/admin/users", message="User deleted successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/admin/users", message=str(exc), level="error")


@router.get("/courses", name="admin_courses")
def courses_page(
    request: Request,
    search: str | None = Query(default=None),
    active: str | None = Query(default=None),
    edit: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    service = AdminService(db)
    courses, total = service.list_courses(
        search=search,
        is_active=_parse_active_filter(active),
        page=page,
        page_size=10,
    )
    edit_course = service.academic_repo.get_course(edit) if edit else None
    return render_template(
        request,
        "admin/courses.html",
        title="Manage Courses",
        current_user=current_user,
        courses=courses,
        total=total,
        pager=pagination(page, 10, total),
        edit_course=edit_course,
        search=search or "",
        active_filter=active or "",
    )


@router.post("/courses", name="admin_courses_create")
def create_course(
    request: Request,
    csrf_token: str = Form(...),
    title: str = Form(...),
    slug: str = Form(default=""),
    description: str = Form(...),
    duration_weeks: int = Form(...),
    price: int = Form(...),
    is_active: bool = Form(default=True),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        AdminService(db).create_course(
            CourseCreate(
                title=title,
                slug=slug or None,
                description=description,
                duration_weeks=duration_weeks,
                price=price,
                is_active=is_active,
            ),
            actor_id=current_user.id,
        )
        return redirect_with_flash(request, "/admin/courses", message="Course created successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/admin/courses", message=str(exc), level="error")


@router.post("/courses/{course_id}/update", name="admin_courses_update")
def update_course(
    course_id: int,
    request: Request,
    csrf_token: str = Form(...),
    title: str = Form(default=""),
    slug: str = Form(default=""),
    description: str = Form(default=""),
    duration_weeks: int = Form(...),
    price: int = Form(...),
    is_active: bool = Form(default=False),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        AdminService(db).update_course(
            course_id,
            CourseUpdate(
                title=title or None,
                slug=slug or None,
                description=description or None,
                duration_weeks=duration_weeks,
                price=price,
                is_active=is_active,
            ),
            actor_id=current_user.id,
        )
        return redirect_with_flash(request, "/admin/courses", message="Course updated successfully.")
    except Exception as exc:
        return redirect_with_flash(request, f"/admin/courses?edit={course_id}", message=str(exc), level="error")


@router.post("/courses/{course_id}/delete", name="admin_courses_delete")
def delete_course(
    course_id: int,
    request: Request,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        AdminService(db).delete_course(course_id, actor_id=current_user.id)
        return redirect_with_flash(request, "/admin/courses", message="Course deleted successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/admin/courses", message=str(exc), level="error")


@router.get("/enrollments", name="admin_enrollments")
def enrollments_page(
    request: Request,
    search: str | None = Query(default=None),
    teacher_id: int | None = Query(default=None),
    student_id: int | None = Query(default=None),
    course_id: int | None = Query(default=None),
    edit: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    service = AdminService(db)
    enrollments, total = service.list_enrollments(
        search=search,
        teacher_id=teacher_id,
        student_id=student_id,
        course_id=course_id,
        page=page,
        page_size=10,
    )
    return render_template(
        request,
        "admin/enrollments.html",
        title="Manage Enrollments",
        current_user=current_user,
        enrollments=enrollments,
        total=total,
        pager=pagination(page, 10, total),
        teachers=service.teacher_options(),
        students=service.student_options(),
        courses=service.course_options(),
        edit_enrollment=service.academic_repo.get_enrollment(edit) if edit else None,
        search=search or "",
        teacher_filter=teacher_id,
        student_filter=student_id,
        course_filter=course_id,
    )


@router.post("/enrollments", name="admin_enrollments_create")
def create_enrollment(
    request: Request,
    csrf_token: str = Form(...),
    student_id: int = Form(...),
    teacher_id: int = Form(...),
    course_id: int = Form(...),
    status: str = Form(...),
    start_date: str = Form(default=""),
    meeting_link: str = Form(default=""),
    notes: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        AdminService(db).create_enrollment(
            EnrollmentCreate(
                student_id=student_id,
                teacher_id=teacher_id,
                course_id=course_id,
                status=status,
                start_date=parse_date_input(start_date),
                meeting_link=meeting_link or None,
                notes=notes or None,
            ),
            actor_id=current_user.id,
        )
        return redirect_with_flash(request, "/admin/enrollments", message="Enrollment created successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/admin/enrollments", message=str(exc), level="error")


@router.post("/enrollments/{enrollment_id}/update", name="admin_enrollments_update")
def update_enrollment(
    enrollment_id: int,
    request: Request,
    csrf_token: str = Form(...),
    teacher_id: int = Form(...),
    course_id: int = Form(...),
    status: str = Form(...),
    start_date: str = Form(default=""),
    progress_percent: int = Form(default=0),
    meeting_link: str = Form(default=""),
    notes: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        AdminService(db).update_enrollment(
            enrollment_id,
            EnrollmentUpdate(
                teacher_id=teacher_id,
                course_id=course_id,
                status=status,
                start_date=parse_date_input(start_date),
                progress_percent=progress_percent,
                meeting_link=meeting_link or None,
                notes=notes or None,
            ),
            actor_id=current_user.id,
        )
        return redirect_with_flash(request, "/admin/enrollments", message="Enrollment updated successfully.")
    except Exception as exc:
        return redirect_with_flash(
            request,
            f"/admin/enrollments?edit={enrollment_id}",
            message=str(exc),
            level="error",
        )


@router.post("/enrollments/{enrollment_id}/delete", name="admin_enrollments_delete")
def delete_enrollment(
    enrollment_id: int,
    request: Request,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        AdminService(db).delete_enrollment(enrollment_id, actor_id=current_user.id)
        return redirect_with_flash(request, "/admin/enrollments", message="Enrollment removed successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/admin/enrollments", message=str(exc), level="error")


@router.get("/assignments", name="admin_assignments")
def assignments_page(
    request: Request,
    search: str | None = Query(default=None),
    teacher_id: int | None = Query(default=None),
    course_id: int | None = Query(default=None),
    edit: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    service = AdminService(db)
    assignments, total = service.list_assignments(
        search=search,
        teacher_id=teacher_id,
        course_id=course_id,
        page=page,
        page_size=10,
    )
    return render_template(
        request,
        "admin/assignments.html",
        title="Manage Assignments",
        current_user=current_user,
        assignments=assignments,
        total=total,
        pager=pagination(page, 10, total),
        teachers=service.teacher_options(),
        courses=service.course_options(),
        edit_assignment=service.academic_repo.get_assignment(edit) if edit else None,
        search=search or "",
        teacher_filter=teacher_id,
        course_filter=course_id,
    )


@router.post("/assignments", name="admin_assignments_create")
async def create_assignment(
    request: Request,
    csrf_token: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    course_id: int = Form(...),
    teacher_id: int = Form(...),
    due_at: str = Form(default=""),
    max_score: int = Form(default=100),
    attachment: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        attachment_url = None
        if attachment and attachment.filename:
            attachment_url = (
                await SupabaseStorageService().upload_file(
                    attachment,
                    folder="admin-assignments",
                    owner_id=current_user.id,
                )
            ).file_url
        AdminService(db).create_assignment(
            AssignmentAdminCreate(
                title=title,
                description=description,
                course_id=course_id,
                teacher_id=teacher_id,
                due_at=parse_datetime_input(due_at),
                max_score=max_score,
                attachment_url=attachment_url,
            ),
            actor_id=current_user.id,
        )
        return redirect_with_flash(request, "/admin/assignments", message="Assignment created successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/admin/assignments", message=str(exc), level="error")


@router.post("/assignments/{assignment_id}/update", name="admin_assignments_update")
async def update_assignment(
    assignment_id: int,
    request: Request,
    csrf_token: str = Form(...),
    title: str = Form(default=""),
    description: str = Form(default=""),
    course_id: int = Form(...),
    teacher_id: int = Form(...),
    due_at: str = Form(default=""),
    max_score: int = Form(default=100),
    attachment: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        assignment = AdminService(db).academic_repo.get_assignment(assignment_id)
        attachment_url = assignment.attachment_url if assignment else None
        if attachment and attachment.filename:
            attachment_url = (
                await SupabaseStorageService().upload_file(
                    attachment,
                    folder="admin-assignments",
                    owner_id=current_user.id,
                )
            ).file_url
        AdminService(db).update_assignment(
            assignment_id,
            AssignmentAdminUpdate(
                title=title or None,
                description=description or None,
                course_id=course_id,
                teacher_id=teacher_id,
                due_at=parse_datetime_input(due_at),
                max_score=max_score,
                attachment_url=attachment_url,
            ),
            actor_id=current_user.id,
        )
        return redirect_with_flash(request, "/admin/assignments", message="Assignment updated successfully.")
    except Exception as exc:
        return redirect_with_flash(
            request,
            f"/admin/assignments?edit={assignment_id}",
            message=str(exc),
            level="error",
        )


@router.post("/assignments/{assignment_id}/delete", name="admin_assignments_delete")
def delete_assignment(
    assignment_id: int,
    request: Request,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    try:
        validate_csrf(request, csrf_token)
        AdminService(db).delete_assignment(assignment_id, actor_id=current_user.id)
        return redirect_with_flash(request, "/admin/assignments", message="Assignment deleted successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/admin/assignments", message=str(exc), level="error")


@router.get("/logs", name="admin_logs")
def logs_page(
    request: Request,
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN)),
):
    service = AdminService(db)
    logs, total = service.list_logs(search=search, page=page, page_size=20)
    return render_template(
        request,
        "admin/logs.html",
        title="Activity Logs",
        current_user=current_user,
        logs=logs,
        total=total,
        pager=pagination(page, 20, total),
        search=search or "",
    )
