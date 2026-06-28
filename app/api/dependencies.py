from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models import User, UserRole
from app.services.auth import AuthService


settings = get_settings()


def _extract_token(authorization: str | None, request: Request) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    return request.cookies.get(settings.access_cookie_name)


def require_api_user(*roles: UserRole):
    def dependency(
        request: Request,
        db: Session = Depends(get_db),
        authorization: str | None = Header(default=None),
    ) -> User:
        token = _extract_token(authorization, request)
        if not token:
            raise HTTPException(status_code=401, detail="Authentication required.")

        try:
            user = AuthService(db).get_current_user(token)
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

        if roles and user.role not in roles:
            raise HTTPException(status_code=403, detail="You do not have permission for this resource.")
        return user

    return dependency

