import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.database import SessionLocal, init_db
from app.services.vector_store import get_vector_store
from app.models.database_models import Product, Compatibility
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_json(filename):
    """Load JSON file from data directory"""
    data_dir = Path(__file__).parent.parent / "data"
    file_path = data_dir / filename

    with open(file_path, "r") as f:
        return json.load(f)


def seed_products():
    """Seed products into database"""
    db = SessionLocal()

    try:
        # Check if products already exist
        existing_count = db.query(Product).count()
        if existing_count > 0:
            logger.info(
                f"Database already contains {existing_count} products. Skipping seed."
            )
            return

        # Load products from JSON
        data = load_json("products.json")
        products = data["products"]

        # Add products to database
        for product_data in products:
            product = Product(
                part_number=product_data["part_number"],
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                image_url=product_data["image_url"],
                category=product_data["category"],
                appliance_type=product_data["appliance_type"],
                brand=product_data["brand"],
                in_stock=product_data["in_stock"],
            )
            db.add(product)

        db.commit()
        logger.info(f"Successfully seeded {len(products)} products")

    except Exception as e:
        logger.error(f"Error seeding products: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def seed_compatibility():
    """Seed compatibility data into database"""
    db = SessionLocal()

    try:
        # Check if compatibility data already exists
        existing_count = db.query(Compatibility).count()
        if existing_count > 0:
            logger.info(
                f"Database already contains {existing_count} compatibility records. Skipping seed."
            )
            return

        # Load compatibility data
        data = load_json("compatibility.json")
        compatibility_data = data["compatibility"]

        # Add compatibility records
        for compat_data in compatibility_data:
            part_number = compat_data["part_number"]

            # Find product
            product = (
                db.query(Product).filter(Product.part_number == part_number).first()
            )

            if not product:
                logger.warning(
                    f"Product {part_number} not found, skipping compatibility"
                )
                continue

            # Add compatibility for each model
            for model_number in compat_data["model_numbers"]:
                compatibility = Compatibility(
                    product_id=product.id,
                    model_number=model_number.upper(),
                    brand=compat_data["brand"],
                    appliance_type=compat_data["appliance_type"],
                )
                db.add(compatibility)

        db.commit()
        logger.info("Successfully seeded compatibility data")

    except Exception as e:
        logger.error(f"Error seeding compatibility: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def seed_vector_store():
    """Seed vector store with products and troubleshooting docs"""
    try:
        vector_store = get_vector_store()

        # Load and add products
        data = load_json("products.json")
        products = data["products"]
        vector_store.add_products(products)
        logger.info(f"Added {len(products)} products to vector store")

        # Load and add troubleshooting docs
        data_dir = Path(__file__).parent.parent / "data" / "troubleshooting"
        troubleshooting_docs = []

        for txt_file in data_dir.glob("*.txt"):
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

                troubleshooting_docs.append(
                    {
                        "title": title or txt_file.stem,
                        "content": content,
                        "category": category,
                        "appliance_type": appliance_type,
                    }
                )

        vector_store.add_troubleshooting_docs(troubleshooting_docs)
        logger.info(
            f"Added {len(troubleshooting_docs)} troubleshooting docs to vector store"
        )

    except Exception as e:
        logger.error(f"Error seeding vector store: {e}")
        raise


def main():
    """Main seeding function"""
    logger.info("Starting database seeding...")

    # Initialize database
    init_db()

    # Seed data
    seed_products()
    seed_compatibility()
    seed_vector_store()

    logger.info("Database seeding complete!")


if __name__ == "__main__":
    main()
