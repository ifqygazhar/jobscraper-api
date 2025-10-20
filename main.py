from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.routes import router
import uvicorn

# Buat aplikasi FastAPI
app = FastAPI(
    title="Job Scraper API",
    description="API untuk scraping lowongan pekerjaan dari berbagai platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Untuk production, ganti dengan domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root ke dokumentasi API"""
    return RedirectResponse(url="/docs")


@app.get("/api", include_in_schema=False)
async def api_root():
    """Root endpoint untuk API"""
    return {
        "message": "Welcome to Job Scraper API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
