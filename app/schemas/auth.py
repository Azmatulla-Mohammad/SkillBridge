from pydantic import BaseModel, ConfigDict

from app.models import UserRole


class LoginRequest(BaseModel):
    email: str
    password: str


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    role: UserRole
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSummary

