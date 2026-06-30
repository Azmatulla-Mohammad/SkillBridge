from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import require_api_user
from app.core.config import get_settings
from app.core.database import get_db
from app.models import UserRole
from app.services.execution.execution_provider import ExecutionProvider
from app.services.execution.execution_service import ExecutionService
from app.services.execution.providers.piston_provider import PistonProvider

router = APIRouter(
    prefix="/practice-lab",
    tags=["api-practice-lab"],
)



class PracticeLabRunRequest(BaseModel):
    question_id: int
    code: str

    stdin: str = ""
    timeout: int | None = 5


@router.post("/run")
async def run_practice_lab(
    payload: PracticeLabRunRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(require_api_user(UserRole.STUDENT)),
):
    settings = get_settings()

    provider_name = settings.CODE_EXECUTION_PROVIDER.lower()



    provider: ExecutionProvider

    if provider_name == "local_python":
        from app.services.execution.providers.local_python_provider import LocalPythonProvider
        provider = LocalPythonProvider()

    elif provider_name == "piston":
        provider = PistonProvider()

    else:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Unsupported execution provider: {provider_name}",
            "exit_code": None,
            "execution_time": 0,
        }




    service = ExecutionService(provider)
    return await service.run_python(code=payload.code, stdin=payload.stdin, timeout=payload.timeout or 5)

