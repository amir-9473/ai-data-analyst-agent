from fastapi import APIRouter, HTTPException

from app.agent.orchestrator import run_agent
from app.loaders.pandas_loader import load_data
from app.schemas.analysis_schema import AnalyzeRequest, AnalyzeResponse
from app.services.file_service import get_file_path
from app.llm.service_errors import ExternalServiceError, friendly_error


router = APIRouter(prefix="/analyze", tags=["Analysis"])


@router.post("/", response_model=AnalyzeResponse)
def analyze_dataset(request: AnalyzeRequest):
    try:
        result = run_agent(load_data(get_file_path(request.file_id)), request.question)
        return {"file_id": request.file_id, "question": request.question, **result.model_dump()}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Dataset file not found.") from exc
    except ExternalServiceError as exc:
        status = 429 if exc.status == 429 else 504 if exc.kind == "timeout" else 503
        raise HTTPException(status_code=status, detail=friendly_error(exc)) from None
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=friendly_error(exc)) from None
