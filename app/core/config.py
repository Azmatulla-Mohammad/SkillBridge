from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SkillBridge"
    app_url: str = "http://127.0.0.1:8000"
    environment: str = "development"
    secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 720
    database_url: str = "sqlite:///./skillbridge.db"
    auto_create_schema: bool = True
    secure_cookies: bool = False
    session_cookie_name: str = "skillbridge_session"
    access_cookie_name: str = "skillbridge_token"
    max_upload_size_mb: int = 20
    allowed_upload_extensions: str = "pdf,doc,docx,ppt,pptx,zip,png,jpg,jpeg,webp"
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    supabase_bucket: str = "skillbridge"
    whatsapp_number: str = "919999999999"
    admin_bootstrap_email: str | None = None
    admin_bootstrap_password: str | None = None
    admin_bootstrap_name: str = "Platform Admin"
    default_course_title: str = "Python Programming"
    default_course_slug: str = "python-programming"
    default_course_description: str = (
        "A one-to-one Python learning journey focused on foundations, problem solving, "
        "assignments, and live mentorship."
    )
    default_course_duration_weeks: int = 12
    default_course_price: int = 4999

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def upload_extensions(self) -> set[str]:
        return {
            extension.strip().lower().lstrip(".")
            for extension in self.allowed_upload_extensions.split(",")
            if extension.strip()
        }

    @property
    def public_whatsapp_number(self) -> str:
        number = self.whatsapp_number.strip()
        placeholder_numbers = {"919999999999", "999999999999", "0000000000"}
        return "" if not number or number in placeholder_numbers else number

    @property
    def templates_dir(self) -> Path:
        return BASE_DIR / "app" / "templates"

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "app" / "static"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
