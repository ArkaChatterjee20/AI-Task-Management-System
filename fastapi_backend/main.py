from fastapi import FastAPI

from fastapi_backend.routers.analytics import (
    router as analytics_router,
)
from fastapi_backend.routers.tasks import (
    router as tasks_router,
)
from fastapi_backend.routers.pipeline import (
    router as pipeline_router,
)
from fastapi_backend.exceptions import (
    global_exception_handler,
)
from fastapi_backend.routers import ml_predictions
from fastapi_backend.routers import prediction_history
from fastapi_backend.routers import auth
from fastapi_backend.routers import user_tasks

app = FastAPI(
    title="AI Task Management API",
    description="Backend API for the AI Task Management ELT pipeline",
    version="1.0.0",
)
app.add_exception_handler(
    Exception,
    global_exception_handler,
)

app.include_router(analytics_router)
app.include_router(tasks_router)
app.include_router(pipeline_router)
app.include_router(ml_predictions.router)
app.include_router(prediction_history.router)
app.include_router(auth.router)
app.include_router(user_tasks.router)


@app.get("/")
def home():
    return {
        "message": "AI Task Management API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }