from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import StudentProfile, TeacherProfile, User, UserRole


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .options(joinedload(User.teacher_profile), joinedload(User.student_profile))
            .where(User.id == user_id)
        )
        return self.db.scalar(stmt)

    def get_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .options(joinedload(User.teacher_profile), joinedload(User.student_profile))
            .where(User.email == email.lower().strip())
        )
        return self.db.scalar(stmt)

    def list_users(
        self,
        *,
        role: UserRole | None = None,
        search: str | None = None,
        is_active: bool | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[User], int]:
        stmt = select(User).options(
            joinedload(User.teacher_profile),
            joinedload(User.student_profile),
        )
        if role:
            stmt = stmt.where(User.role == role)
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
        if search:
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    User.full_name.ilike(term),
                    User.email.ilike(term),
                    User.phone.ilike(term),
                )
            )

        total = self.db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(User.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
            .unique()
            .all()
        )
        return items, total

    def role_counts(self) -> dict[str, int]:
        stmt = select(User.role, func.count(User.id)).group_by(User.role)
        return {role.value: count for role, count in self.db.execute(stmt).all()}

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def create_teacher_profile(self, profile: TeacherProfile) -> TeacherProfile:
        self.db.add(profile)
        self.db.flush()
        return profile

    def create_student_profile(self, profile: StudentProfile) -> StudentProfile:
        self.db.add(profile)
        self.db.flush()
        return profile

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.flush()

