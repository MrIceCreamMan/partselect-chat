# scripts/check_all_data.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.database import SessionLocal
from app.services.vector_store import get_vector_store
from app.models.database_models import Product, Compatibility
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_all():
    # Check database
    db = SessionLocal()
    products_count = db.query(Product).count()
    compat_count = db.query(Compatibility).count()
    logger.info(f"Database - Products: {products_count}, Compatibility: {compat_count}")
    db.close()

    # Check vector store
    vector_store = get_vector_store()
    vs_products = vector_store.products_collection.count()
    vs_troubleshooting = vector_store.troubleshooting_collection.count()
    logger.info(
        f"Vector Store - Products: {vs_products}, Troubleshooting: {vs_troubleshooting}"
    )

    if vs_troubleshooting > 0:
        sample = vector_store.troubleshooting_collection.get(limit=1)
        logger.info(f"Sample troubleshooting doc: {sample['metadatas'][0]}")


if __name__ == "__main__":
    check_all()
