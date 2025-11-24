# scripts/seed_vector_only.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.vector_store import get_vector_store
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_vector_store():
    """Seed vector store with products and troubleshooting docs"""
    try:
        logger.info("Initializing vector store...")
        vector_store = get_vector_store()

        # Load and add products
        logger.info("Loading products...")
        data_dir = Path(__file__).parent.parent / "data"
        products_file = data_dir / "products.json"

        with open(products_file, "r") as f:
            data = json.load(f)
            products = data["products"]

        logger.info(f"Adding {len(products)} products to vector store...")
        vector_store.add_products(products)
        logger.info(f"✓ Added {len(products)} products to vector store")

        # Load and add troubleshooting docs
        logger.info("Loading troubleshooting docs...")
        troubleshooting_dir = data_dir / "troubleshooting"

        # Check if directory exists
        if not troubleshooting_dir.exists():
            logger.error(f"Troubleshooting directory not found: {troubleshooting_dir}")
            return

        txt_files = list(troubleshooting_dir.glob("*.txt"))
        logger.info(f"Found {len(txt_files)} .txt files in {troubleshooting_dir}")

        troubleshooting_docs = []
        for txt_file in txt_files:
            logger.info(f"Processing: {txt_file.name}")
            with open(txt_file, "r") as f:
                content = f.read()

                # Extract metadata from content
                lines = content.split("\n")
                title = ""
                category = "general"
                appliance_type = "general"

                for line in lines[:10]:  # Check first 10 lines for metadata
                    if line.startswith("Title:"):
                        title = line.replace("Title:", "").strip()
                    elif line.startswith("Category:"):
                        category = line.replace("Category:", "").strip()
                    elif line.startswith("Appliance:"):
                        appliance_type = line.replace("Appliance:", "").strip().lower()

                doc = {
                    "title": title or txt_file.stem,
                    "content": content,
                    "category": category,
                    "appliance_type": appliance_type,
                }
                troubleshooting_docs.append(doc)
                logger.info(
                    f"  - Title: {doc['title']}, Category: {doc['category']}, Appliance: {doc['appliance_type']}"
                )

        if troubleshooting_docs:
            logger.info(
                f"Adding {len(troubleshooting_docs)} troubleshooting docs to vector store..."
            )
            vector_store.add_troubleshooting_docs(troubleshooting_docs)
            logger.info(
                f"✓ Added {len(troubleshooting_docs)} troubleshooting docs to vector store"
            )
        else:
            logger.warning("No troubleshooting docs found!")

        # Verify what was added
        logger.info("\n=== Verification ===")
        products_count = vector_store.products_collection.count()
        troubleshooting_count = vector_store.troubleshooting_collection.count()
        logger.info(f"Products in vector store: {products_count}")
        logger.info(f"Troubleshooting docs in vector store: {troubleshooting_count}")

    except Exception as e:
        logger.error(f"Error seeding vector store: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    seed_vector_store()
