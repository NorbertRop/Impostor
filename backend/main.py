import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import config
from firestore_client import initialize_firebase
from api.rooms import router as rooms_router
from bot.bot import start_bot
import bot.commands  # Import to register commands

# Initialize Firebase
initialize_firebase()

# Create FastAPI app
app = FastAPI(
    title="Impostor Game API",
    description="Backend API for Impostor multiplayer game with Discord integration",
    version="1.0.0"
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
        "service": "impostor-backend",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "Impostor Game Backend API",
        "docs": "/docs",
        "health": "/health"
    }

async def run_bot_async():
    """Run Discord bot"""
    try:
        await start_bot()
    except Exception as e:
        print(f"❌ Bot error: {e}")

async def run_api_async():
    """Run FastAPI server"""
    config_uvicorn = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=config.PORT,
        log_level="info"
    )
    server = uvicorn.Server(config_uvicorn)
    await server.serve()

async def main():
    """Run both bot and API concurrently"""
    print("🚀 Starting Impostor Backend...")
    print(f"📡 API will run on port {config.PORT}")
    print(f"🤖 Discord bot is initializing...")
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Run both services concurrently
    await asyncio.gather(
        run_bot_async(),
        run_api_async()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

