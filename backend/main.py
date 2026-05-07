from fastapi import FastAPI

from backend.routes.auth_routes import router as auth_router
from backend.routes.sync_routes import router as sync_router
from backend.routes.health_routes import router as health_router

app = FastAPI(title="APP MEI SaaS Backend")

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(sync_router)
