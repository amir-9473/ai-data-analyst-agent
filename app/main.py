from fastapi import FastAPI
from app.api.upload import router as upload_router

from app.api.routes import router
from app.api.dataset import router as dataset_router
from app.api.profile import router as profile_router

app = FastAPI(
    title="AI Data Analyst Agent",
    description="AI assistant for analyzing uploaded datasets",
    version="0.1.0"
)

app.include_router(profile_router)

app.include_router(upload_router)
app.include_router(router)
app.include_router(
    dataset_router
)
from fastapi import FastAPI

from app.api.routes import router
from app.api.upload import router as upload_router
from app.api.dataset import router as dataset_router


app = FastAPI(
    title="AI Data Analyst Agent",
    description="AI assistant for analyzing uploaded datasets",
    version="0.1.0"
)


app.include_router(router)

app.include_router(
    upload_router
)

app.include_router(
    dataset_router
)

