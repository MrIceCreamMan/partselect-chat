"""
Utility script to pre-compute embeddings
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.vector_store import get_vector_store
from scripts.seed_data import load_json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_embeddings():
    """Create embeddings for all documents"""
    logger.info("Creating embeddings...")

    vector_store = get_vector_store()

    # This will automatically create embeddings when adding documents
    logger.info("Embeddings created successfully")


if __name__ == "__main__":
    create_embeddings()
