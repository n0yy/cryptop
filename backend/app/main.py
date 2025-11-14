from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.api import alerts, analysis, portfolio, backtest, content, community, risk
from app.websocket.server import websocket_manager
from app.utils.logger import setup_logger

settings = get_settings()
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Crypto Monitoring System...")
    yield
    logger.info("Shutting down Crypto Monitoring System...")
    await websocket_manager.disconnect_all()


app = FastAPI(
    title="Crypto Monitoring & Analysis System",
    description="AI-powered cryptocurrency monitoring and analysis platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(portfolio.router, prefix="/api/portfolios", tags=["Portfolio"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtesting"])
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(community.router, prefix="/api/community", tags=["Community"])
app.include_router(risk.router, prefix="/api/risk", tags=["Risk"])


@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Crypto Monitoring & Analysis System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "success",
        "data": {
            "service": "healthy",
            "environment": settings.ENVIRONMENT
        }
    }


@app.websocket("/ws/alerts/{user_id}")
async def websocket_alerts_endpoint(websocket: WebSocket, user_id: int):
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            await websocket_manager.handle_message(user_id, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)
        logger.info(f"WebSocket disconnected for user {user_id}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )

# Celery integration
if settings.ENVIRONMENT != "production":
    from app.celery_app import celery_app
    celery_app.autodiscover_tasks()
