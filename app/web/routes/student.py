from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import UserRole
from app.schemas.student import StudentProfileUpdate
from app.services.student import StudentService
from app.web.dependencies import (
    pagination,
    redirect_with_flash,
    render_template,
    require_web_user,
    validate_csrf,
)


router = APIRouter(prefix="/student", tags=["web-student"])


@router.get("", name="student_dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.STUDENT)),
):
    context = StudentService(db).dashboard(current_user.id)
    return render_template(
        request,
        "student/dashboard.html",
        title="Student Dashboard",
        current_user=current_user,
        **context,
    )


@router.get("/course", name="student_course")
def course_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.STUDENT)),
):
    context = StudentService(db).dashboard(current_user.id)
    return render_template(
        request,
        "student/course.html",
        title="My Course",
        current_user=current_user,
        **context,
    )


@router.get("/materials", name="student_materials")
def materials_page(
    request: Request,
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.STUDENT)),
):
    materials, total = StudentService(db).list_materials(current_user.id, page=page, page_size=10)
    return render_template(
        request,
        "student/materials.html",
        title="Materials",
        current_user=current_user,
        materials=materials,
        total=total,
        pager=pagination(page, 10, total),
    )


@router.get("/assignments", name="student_assignments")
def assignments_page(
    request: Request,
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.STUDENT)),
):
    service = StudentService(db)
    assignments, total = service.list_assignments(current_user.id, page=page, page_size=10)
    submissions, _ = service.list_feedback(current_user.id, page=1, page_size=200)
    submission_map = {submission.assignment_id: submission for submission in submissions}
    return render_template(
        request,
        "student/assignments.html",
        title="Assignments",
        current_user=current_user,
        assignments=assignments,
        submission_map=submission_map,
        total=total,
        pager=pagination(page, 10, total),
    )


@router.post("/assignments/{assignment_id}/submit", name="student_assignments_submit")
async def submit_assignment(
    assignment_id: int,
    request: Request,
    csrf_token: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.STUDENT)),
):
    try:
        validate_csrf(request, csrf_token)
        await StudentService(db).submit_assignment(current_user.id, assignment_id, file)
        return redirect_with_flash(request, "/student/assignments", message="Assignment submitted successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/student/assignments", message=str(exc), level="error")


@router.get("/feedback", name="student_feedback")
def feedback_page(
    request: Request,
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.STUDENT)),
):
    submissions, total = StudentService(db).list_feedback(current_user.id, page=page, page_size=10)
    return render_template(
        request,
        "student/feedback.html",
        title="Feedback",
        current_user=current_user,
        submissions=submissions,
        total=total,
        pager=pagination(page, 10, total),
    )


@router.get("/meetings", name="student_meetings")
def meetings_page(
    request: Request,
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.STUDENT)),
):
    meetings, total = StudentService(db).list_meetings(current_user.id, page=page, page_size=10)
    return render_template(
        request,
        "student/meetings.html",
        title="Meetings",
        current_user=current_user,
        meetings=meetings,
        total=total,
        pager=pagination(page, 10, total),
    )


@router.get("/announcements", name="student_announcements")
def announcements_page(
    request: Request,
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.STUDENT)),
):
    announcements, total = StudentService(db).list_announcements(current_user.id, page=page, page_size=10)
    return render_template(
        request,
        "student/announcements.html",
        title="Announcements",
        current_user=current_user,
        announcements=announcements,
        total=total,
        pager=pagination(page, 10, total),
    )


@router.get("/profile", name="student_profile")
def profile_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.STUDENT)),
):
    user = StudentService(db).user_repo.get(current_user.id)
    return render_template(
        request,
        "student/profile.html",
        title="Student Profile",
        current_user=current_user,
        profile_user=user,
    )


@router.post("/profile", name="student_profile_update")
def update_profile(
    request: Request,
    csrf_token: str = Form(...),
    full_name: str = Form(default=""),
    phone: str = Form(default=""),
    bio: str = Form(default=""),
    guardian_name: str = Form(default=""),
    learning_goals: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.STUDENT)),
):
    try:
        validate_csrf(request, csrf_token)
        StudentService(db).update_profile(
            current_user.id,
            StudentProfileUpdate(
                full_name=full_name or None,
                phone=phone or None,
                bio=bio or None,
                guardian_name=guardian_name or None,
                learning_goals=learning_goals or None,
            ),
        )
        return redirect_with_flash(request, "/student/profile", message="Profile updated successfully.")
    except Exception as exc:
        return redirect_with_flash(request, "/student/profile", message=str(exc), level="error")


@router.get("/practice-lab", name="student_practice_lab")
def practice_lab_home(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.STUDENT)),
):
    from app.services.practice_lab import PracticeLabService

    topics = PracticeLabService(db).list_topics(student_id=current_user.id)
    return render_template(
        request,
        "student/practice_lab_home.html",
        title="Practice Lab",
        current_user=current_user,
        topics=topics,
    )


@router.get("/practice-lab/topic/{topic_id}", name="student_practice_lab_topic")
def practice_lab_topic_page(
    request: Request,
    topic_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.STUDENT)),
):
    from app.services.practice_lab import PracticeLabService

    service = PracticeLabService(db)
    topic = service.get_topic(topic_id)
    if not topic:
        from fastapi.responses import RedirectResponse

        return RedirectResponse(url="/student/practice-lab", status_code=303)

    question = service.get_first_question(topic_id=topic_id)
    if not question:
        from fastapi.responses import RedirectResponse

        return RedirectResponse(url="/student/practice-lab", status_code=303)

    return render_template(
        request,
        "student/practice_lab_topic.html",
        title=f"{topic.topic_name}",
        current_user=current_user,
        topic=topic,
        question=question,
    )

