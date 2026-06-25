from fastapi import FastAPI

from api.routers.health import router as health_router
from api.routers.metrics import router as metrics_router
from api.routers.retention import router as retention_router

app = FastAPI(

    title="Customer Retention Intelligence API",

    version="2.0.0"

)

app.include_router(health_router)

app.include_router(metrics_router)

app.include_router(retention_router)