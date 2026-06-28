from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.core.utils import utcnow
from app.models import User
from app.repositories.users import UserRepository
from app.schemas.auth import TokenResponse, UserSummary


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    def authenticate(self, email: str, password: str) -> tuple[str, User]:
        user = self.user_repo.get_by_email(email.lower().strip())
        if not user or not verify_password(password, user.password_hash):
            raise PermissionError("Invalid email or password.")
        if not user.is_active:
            raise PermissionError("This account has been deactivated.")

        user.last_login_at = utcnow()
        self.db.commit()
        self.db.refresh(user)
        token = create_access_token(subject=str(user.id), role=user.role.value)
        return token, user

    def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        user = self.user_repo.get(user_id)
        if not user:
            raise LookupError("User not found.")

        if not verify_password(current_password, user.password_hash):
            raise PermissionError("Current password is incorrect.")

        user.password_hash = hash_password(new_password)
        user.temporary_password_required = False
        user.password_changed_at = utcnow()
        self.db.commit()
        self.db.refresh(user)


    def get_current_user(self, token: str) -> User:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if not subject:
            raise PermissionError("Invalid token subject.")

        user = self.user_repo.get(int(subject))
        if not user or not user.is_active:
            raise PermissionError("Your session is no longer valid.")
        return user

    def build_token_response(self, token: str, user: User) -> TokenResponse:
        return TokenResponse(access_token=token, user=UserSummary.model_validate(user))

