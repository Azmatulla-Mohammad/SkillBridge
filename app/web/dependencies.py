from __future__ import annotations

from datetime import datetime
import math
import secrets

from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models import User, UserRole
from app.services.auth import AuthService


settings = get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))


def format_datetime(value: datetime | None, fmt: str = "%d %b %Y, %I:%M %p") -> str:
    if not value:
        return "TBD"
    return value.strftime(fmt)


def format_currency(value: int | None) -> str:
    return f"\u20b9{value or 0:,}"


templates.env.filters["datetime"] = format_datetime
templates.env.filters["currency"] = format_currency


def get_or_create_csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token


def validate_csrf(request: Request, token: str) -> None:
    expected = get_or_create_csrf_token(request)
    if not token or not secrets.compare_digest(expected, token):
        raise PermissionError("The form session expired. Please refresh the page and try again.")


def flash(request: Request, message: str, level: str = "success") -> None:
    request.session.setdefault("_flashes", []).append({"message": message, "level": level})


def consume_flashes(request: Request) -> list[dict[str, str]]:
    flashes = request.session.pop("_flashes", [])
    return flashes if isinstance(flashes, list) else []


def role_home(user: User) -> str:
    if user.role == UserRole.ADMIN:
        return "/admin"
    if user.role == UserRole.TEACHER:
        return "/teacher"
    return "/student"


def render_template(
    request: Request,
    template_name: str,
    *,
    title: str,
    current_user: User | None = None,
    status_code: int = 200,
    **context,
):
    payload = {
        "request": request,
        "title": title,
        "current_user": current_user,
        "csrf_token": get_or_create_csrf_token(request),
        "flashes": consume_flashes(request),
        "active_path": request.url.path,
        "app_name": settings.app_name,
        "whatsapp_number": settings.public_whatsapp_number,
        "has_whatsapp_number": bool(settings.public_whatsapp_number),
        **context,
    }
    return templates.TemplateResponse(template_name, payload, status_code=status_code)


def redirect_with_flash(
    request: Request,
    location: str,
    *,
    message: str | None = None,
    level: str = "success",
) -> RedirectResponse:
    if message:
        flash(request, message, level)
    return RedirectResponse(url=location, status_code=303)


def parse_date_input(value: str | None):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_datetime_input(value: str | None):
    if not value:
        return None
    return datetime.fromisoformat(value)


def pagination(page: int, page_size: int, total: int) -> dict:
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": max(1, math.ceil(total / page_size)) if page_size else 1,
    }


def get_optional_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    token = request.cookies.get(settings.access_cookie_name)
    if not token:
        return None
    try:
        return AuthService(db).get_current_user(token)
    except PermissionError:
        return None


def require_web_user(*roles: UserRole):
    def dependency(request: Request, db: Session = Depends(get_db)) -> User:
        token = request.cookies.get(settings.access_cookie_name)
        if not token:
            raise HTTPException(status_code=303, headers={"Location": "/login"})

        try:
            user = AuthService(db).get_current_user(token)
        except PermissionError as exc:
            raise HTTPException(status_code=303, headers={"Location": "/login"}) from exc

        if roles and user.role not in roles:
            raise HTTPException(status_code=303, headers={"Location": role_home(user)})
        return user

    return dependency
