from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.ai_routes import router as ai_router
from app.utils.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME
)

# =========================
# CORS Configuration
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =========================
# Routers
# =========================

app.include_router(
    ai_router,
    prefix="/api/v1"
)

# =========================
# Root Endpoint
# =========================

@app.get("/")
async def root():
    return {
        "message": f"{settings.APP_NAME} Running"
    }