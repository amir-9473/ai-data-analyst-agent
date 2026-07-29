from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="AI Data Analyst Agent",
    description="AI assistant for analyzing uploaded datasets",
    version="0.1.0"
)


app.include_router(router)