from fastapi import FastAPI

from app.api.analyze import router as analyze_router
from app.api.dataset import router as dataset_router
from app.api.profile import router as profile_router
from app.api.routes import router as health_router
from app.api.upload import router as upload_router


app = FastAPI(
    title="AI Data Analyst Agent",
    description="Multilingual assistant for uploaded datasets",
    version="0.2.0",
)

for router in (health_router, upload_router, dataset_router, profile_router, analyze_router):
    app.include_router(router)
