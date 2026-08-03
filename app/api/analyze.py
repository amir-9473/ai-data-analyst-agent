# ==========================================================
# Analyze API
# ==========================================================

from fastapi import (
    APIRouter,
    HTTPException,
)

from app.agent.orchestrator import (
    run_agent,
)

from app.loaders.pandas_loader import (
    load_data,
)

from app.schemas.analysis_schema import (
    AnalyzeRequest,
)

from app.services.file_service import (
    get_file_path,
)


# ==========================================================
# Router
# ==========================================================

router = APIRouter(
    prefix="/analyze",
    tags=["Analysis"],
)


# ==========================================================
# Analyze Dataset
# ==========================================================

@router.post("/")
def analyze_dataset(
    request: AnalyzeRequest,
):

    """
    Analyze an uploaded dataset
    using the AI data analyst agent.
    """

    try:

        # --------------------------------------------------
        # Get Dataset Path
        # --------------------------------------------------

        file_path = get_file_path(
            request.file_id
        )


        # --------------------------------------------------
        # Load Dataset
        # --------------------------------------------------

        df = load_data(
            file_path
        )


        # --------------------------------------------------
        # Run Agent
        # --------------------------------------------------

        answer = run_agent(

            df=df,

            question=request.question,
        )
        
        print(type(answer))
        print(repr(answer))
        
        print(
            "DEBUG ANSWER:",
            repr(answer),
        )


        # --------------------------------------------------
        # Return Response
        # --------------------------------------------------

        return {

            "file_id": (
                request.file_id
            ),

            "question": (
                request.question
            ),

            "answer": answer,

        }


    except FileNotFoundError:

        raise HTTPException(

            status_code=404,

            detail=(
                "Dataset file "
                "not found."
            ),

        )


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e),

        )