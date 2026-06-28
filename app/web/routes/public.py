from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import InquiryType
from app.services.public import PublicService
from app.web.dependencies import (
    get_optional_current_user,
    redirect_with_flash,
    render_template,
    validate_csrf,
)


router = APIRouter()


@router.get("/", name="home")
def home(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    context = PublicService(db).site_context()
    return render_template(request, "public/home.html", title="SkillBridge", current_user=current_user, **context)


@router.get("/about", name="about")
def about(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    context = PublicService(db).site_context()
    return render_template(request, "public/about.html", title="About SkillBridge", current_user=current_user, **context)


@router.get("/courses", name="courses")
def courses(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    context = PublicService(db).site_context()
    return render_template(request, "public/courses.html", title="Courses", current_user=current_user, **context)


@router.get("/pricing", name="pricing")
def pricing(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    # Pricing page removed from UI/UX redesign.
    # Redirect legacy /pricing route to /courses without changing backend logic.
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/courses", status_code=303)



@router.get("/book-demo", name="book_demo")
def book_demo(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    context = PublicService(db).site_context()
    return render_template(request, "public/book_demo.html", title="Book Free Demo", current_user=current_user, **context)


@router.post("/book-demo", name="book_demo_submit")
def submit_book_demo(
    request: Request,
    csrf_token: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(default=""),
    message: str = Form(...),
    course_interest: str = Form(default=""),
    db: Session = Depends(get_db),
):
    try:
        validate_csrf(request, csrf_token)
        PublicService(db).submit_inquiry(
            inquiry_type=InquiryType.DEMO,
            name=name,
            email=email,
            phone=phone,
            message=message,
            course_interest=course_interest,
        )
        return redirect_with_flash(
            request,
            "/book-demo",
            message="Demo request submitted. The team can now follow up from the admin dashboard.",
        )
    except Exception as exc:
        return redirect_with_flash(request, "/book-demo", message=str(exc), level="error")


@router.get("/contact", name="contact")
def contact(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    context = PublicService(db).site_context()
    return render_template(request, "public/contact.html", title="Contact", current_user=current_user, **context)


@router.post("/contact", name="contact_submit")
def submit_contact(
    request: Request,
    csrf_token: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(default=""),
    message: str = Form(...),
    course_interest: str = Form(default=""),
    db: Session = Depends(get_db),
):
    try:
        validate_csrf(request, csrf_token)
        PublicService(db).submit_inquiry(
            inquiry_type=InquiryType.CONTACT,
            name=name,
            email=email,
            phone=phone,
            message=message,
            course_interest=course_interest,
        )
        return redirect_with_flash(
            request,
            "/contact",
            message="Message sent successfully. It is now visible to the admin team.",
        )
    except Exception as exc:
        return redirect_with_flash(request, "/contact", message=str(exc), level="error")


@router.get("/faq", name="faq")
def faq(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    context = PublicService(db).site_context()
    return render_template(request, "public/faq.html", title="FAQ", current_user=current_user, **context)

