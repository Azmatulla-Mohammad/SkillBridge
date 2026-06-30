from pathlib import Path
from functools import lru_cache

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
    # Use DATABASE_URL for PostgreSQL (and any other supported DB).
    # IMPORTANT: runtime must be driven by env; no SQLite defaults in production.
    database_url: str | None = None

    auto_create_schema: bool = False

    # Development-only flag: if false, SQLAlchemy will not run Base.metadata.create_all() at startup.
    # Read from AUTO_CREATE_SCHEMA env var (auto_create_schema field).


    secure_cookies: bool = False
    session_cookie_name: str = "skillbridge_session"
    access_cookie_name: str = "skillbridge_token"
    max_upload_size_mb: int = 20
    allowed_upload_extensions: str = "pdf,doc,docx,ppt,pptx,zip,png,jpg,jpeg,webp"
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    supabase_bucket: str = "skillbridge"
    whatsapp_number: str = "919999999999"

    # SMTP settings (for email notifications)
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_to: str | None = None

    # Production admin bootstrap (create once)
    default_admin_email: str | None = None
    default_admin_password: str | None = None


    # Backwards-compatible legacy config (no longer used for bootstrap defaults)
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

    # Code execution provider for Practice Lab
    CODE_EXECUTION_PROVIDER: str = "local_python"
    PYTHON_EXECUTION_TIMEOUT: int = 5
    PYTHON_MAX_OUTPUT_SIZE: int = 50000


    @property
    def is_sqlite(self) -> bool:
        return bool(self.database_url) and self.database_url.startswith("sqlite")


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
    settings = Settings()

    import logging

    logger = logging.getLogger(__name__)
    logger.info("auto_create_schema=%s", settings.auto_create_schema)


    # Fail fast: database_url must come from DATABASE_URL env var for PG migration.
    if not settings.database_url:

        raise RuntimeError(
            "DATABASE_URL is not set. Set it to a PostgreSQL DSN like: "
            "postgresql+psycopg://postgres:<password>@localhost:5432/skillbridge"
        )

    return settings

