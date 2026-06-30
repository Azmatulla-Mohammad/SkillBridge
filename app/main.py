from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import admin as api_admin
from app.api.routes import auth as api_auth
from app.api.routes import student as api_student
from app.api.routes import teacher as api_teacher
from app.core.config import get_settings
from app.core.database import SessionLocal, engine
from app.core.logging import configure_logging
from app.models import Base
from app.services.admin import AdminService
from app.web.dependencies import render_template
from app.web.routes import admin as web_admin
from app.web.routes import auth as web_auth
from app.web.routes import public as web_public
from app.web.routes import student as web_student
from app.web.routes import teacher as web_teacher


settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    import logging

    logger = logging.getLogger(__name__)

    logger.info("Starting app (auto_create_schema=%s)", settings.auto_create_schema)


    # Never run schema creation when AUTO_CREATE_SCHEMA=false
    if (
        getattr(settings, "AUTO_CREATE_SCHEMA", False)
        and settings.auto_create_schema
    ):
        logger.info("Running Base.metadata.create_all()")
        Base.metadata.create_all(bind=engine)
    else:
        logger.info("Skipping Base.metadata.create_all()")


    db = SessionLocal()

    try:
        AdminService(db).bootstrap_defaults()
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie=settings.session_cookie_name,
    same_site="lax",
    https_only=settings.secure_cookies,
)
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

app.include_router(web_public.router)
app.include_router(web_auth.router)
app.include_router(web_admin.router)
app.include_router(web_teacher.router)
app.include_router(web_student.router)

app.include_router(api_auth.router, prefix="/api")
app.include_router(api_admin.router, prefix="/api")
app.include_router(api_teacher.router, prefix="/api")
app.include_router(api_student.router, prefix="/api")

from app.api.routes.practice_lab import router as api_practice_lab
app.include_router(api_practice_lab, prefix="/api")


@app.exception_handler(404)
async def not_found_handler(request: Request, _):
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=404, content={"detail": "Resource not found."})
    return render_template(request, "errors/404.html", title="Page Not Found", status_code=404)


@app.exception_handler(500)
async def server_error_handler(request: Request, _):
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=500, content={"detail": "Internal server error."})
    return render_template(request, "errors/500.html", title="Server Error", status_code=500)
