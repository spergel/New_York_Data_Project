from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
import os

# Create FastAPI app
app = FastAPI(
    title="NYC Academic Events API",
    description="API for accessing academic events from NYC universities and institutions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nyc-academic-events-api"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
