import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ==========================================
# 1. APP INITIALIZATION & CONFIGURATION
# ==========================================
app = FastAPI(
    title="Sakura AI Master API",
    description="Enterprise-grade AI Microservice built for high-performance tasks.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ==========================================
# 2. SECURITY & MIDDLEWARE (CORS & Analytics)
# ==========================================
# Allows external apps or websites to securely connect to this AI API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this can be restricted to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for timing requests (Performance Tracking)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# ==========================================
# 3. PYDANTIC MODELS (Strict Data Validation)
# ==========================================
class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str
    uptime_seconds: float

class BaseResponse(BaseModel):
    success: bool
    message: str

# ==========================================
# 4. API ENDPOINTS (Routes)
# ==========================================
START_TIME = time.time()

@app.get("/", response_model=BaseResponse, tags=["Core"])
async def root():
    """Root endpoint to verify the API is reachable."""
    return BaseResponse(
        success=True,
        message="Welcome to Sakura AI Master API. The system is online and highly operational."
    )

@app.get("/api/v1/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    """Advanced health check for monitoring systems and load balancers."""
    try:
        uptime = time.time() - START_TIME
        return HealthResponse(
            status="Operational",
            environment="Production",
            version="1.0.0",
            uptime_seconds=round(uptime, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error during health check")

# ==========================================
# 5. ERROR HANDLING (Global Exception Catcher)
# ==========================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Prevents server crashes by catching all unexpected errors cleanly."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False, 
            "message": "An unexpected error occurred.", 
            "details": str(exc)
        }
    )
