from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models import UserRole
from app.services.auth import AuthService
from app.web.dependencies import (
    get_optional_current_user,
    redirect_with_flash,
    render_template,
    role_home,
    require_web_user,
    validate_csrf,
)


router = APIRouter()
settings = get_settings()


@router.get("/login", name="login")
def login_page(
    request: Request,
    current_user=Depends(get_optional_current_user),
):
    if current_user:
        return RedirectResponse(role_home(current_user), status_code=303)
    return render_template(request, "auth/login.html", title="Login")


@router.post("/login", name="login_submit")
def login_submit(
    request: Request,
    csrf_token: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        validate_csrf(request, csrf_token)
        token, user = AuthService(db).authenticate(email, password)
        redirect_url = "/change-password" if user.temporary_password_required else role_home(user)
        response = RedirectResponse(redirect_url, status_code=303)
        response.set_cookie(
            key=settings.access_cookie_name,
            value=token,
            httponly=True,
            secure=settings.secure_cookies,
            samesite="lax",
            max_age=settings.access_token_expire_minutes * 60,
        )
        return response
    except Exception as exc:
        return redirect_with_flash(request, "/login", message=str(exc), level="error")


@router.post("/logout", name="logout")
def logout(request: Request):
    response = redirect_with_flash(request, "/login", message="You have been logged out.")
    response.delete_cookie(settings.access_cookie_name)
    return response


@router.get("/change-password", name="change_password")
def change_password_page(
    request: Request,
    current_user=Depends(require_web_user(UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT)),
):
    if not current_user.temporary_password_required:
        return RedirectResponse(role_home(current_user), status_code=303)
    return render_template(request, "auth/change_password.html", title="Change Password", user=current_user)


@router.post("/change-password", name="change_password_submit")
def change_password_submit(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_web_user(UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT)),
):
    try:
        validate_csrf(request, csrf_token)
        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if new_password != confirm_password:
            raise ValueError("New password and confirm password do not match.")
        AuthService(db).change_password(current_user.id, current_password, new_password)
        response = RedirectResponse(role_home(current_user), status_code=303)
        return response
    except Exception as exc:
        return redirect_with_flash(
            request,
            "/change-password",
            message=str(exc),
            level="error",
        )



@router.get("/forgot-password", name="forgot_password")
def forgot_password(request: Request):
    return render_template(request, "auth/forgot_password.html", title="Forgot Password")
