from pydantic import BaseModel


class StudentProfileUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    bio: str | None = None
    guardian_name: str | None = None
    learning_goals: str | None = None
