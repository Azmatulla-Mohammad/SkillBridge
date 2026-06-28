from fastapi import APIRouter, Depends, Form, Response
from sqlalchemy.orm import Session

from app.api.dependencies import require_api_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models import UserRole
from app.schemas.auth import TokenResponse
from app.services.auth import AuthService


router = APIRouter(tags=["api-auth"])
settings = get_settings()


@router.post("/auth/login", response_model=TokenResponse)
def login(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    token, user = AuthService(db).authenticate(email, password)
    response.set_cookie(
        key=settings.access_cookie_name,
        value=token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return AuthService(db).build_token_response(token, user)


@router.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(settings.access_cookie_name)
    return {"success": True}


@router.get("/auth/me")
def me(current_user=Depends(require_api_user(UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT))):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role.value,
    }

