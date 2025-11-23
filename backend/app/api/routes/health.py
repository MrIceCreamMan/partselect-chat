from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.database import get_db
from app.services.vector_store import get_vector_store
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    """
    try:
        # Check database
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    try:
        # Check vector store
        vector_store = get_vector_store()
        vector_status = "healthy"
    except Exception as e:
        logger.error(f"Vector store health check failed: {e}")
        vector_status = "unhealthy"

    overall_status = (
        "healthy"
        if db_status == "healthy" and vector_status == "healthy"
        else "unhealthy"
    )

    return {
        "status": overall_status,
        "services": {"database": db_status, "vector_store": vector_status},
    }


@router.get("/health/ready")
async def readiness_check():
    """
    Kubernetes readiness probe
    """
    return {"ready": True}


@router.get("/health/live")
async def liveness_check():
    """
    Kubernetes liveness probe
    """
    return {"alive": True}
