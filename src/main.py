from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth
from core.config import settings

app = FastAPI(title="Lawyers Platform API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# health check
@app.get("/")
def healthcheck():
    return {"status": "ok"}