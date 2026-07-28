from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth, professionals, services, patients, appointments

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
origins = settings.BACKEND_CORS_ORIGINS
if settings.DEBUG:
    origins = origins + ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(professionals.router, prefix="/api/v1/professionals", tags=["Professionals"])
app.include_router(services.router, prefix="/api/v1/services", tags=["Services"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["Appointments"])


@app.get("/")
async def root():
    return {
        "message": "TurnosPro API está funcionando 🚀",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "TurnosPro"}
