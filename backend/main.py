import uvicorn
from api.rooms import router as rooms_router
from config import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firestore_client import initialize_firebase

# Initialize Firebase
initialize_firebase()

# Create FastAPI app
app = FastAPI(
    title="Impostor Game API",
    description="Backend API for Impostor multiplayer game with Discord integration",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rooms_router)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "impostor-backend-api",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    return {
        "message": "Impostor Game Backend API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    print("🚀 Starting Impostor Backend API...")
    print(f"📡 Running on port {config.PORT}")

    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        exit(1)

    try:
        uvicorn.run(app, host="0.0.0.0", port=config.PORT, log_level="info")
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
