from typing import Dict, Any, Optional
import logging
import re

from sqlalchemy import or_

from app.tools.base import BaseTool
from app.services.vector_store import get_vector_store
from app.services.database import SessionLocal
from app.models.database_models import Product

logger = logging.getLogger(__name__)

# Simple heuristic: most appliance part numbers are alphanumeric, 5–12 chars.
PART_NUMBER_PATTERN = re.compile(r"^[A-Z0-9\-]{4,15}$", re.I)


class ProductSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "product_search"

    @property
    def description(self) -> str:
        return "Search for refrigerator or dishwasher parts"

    async def execute(
        self, query: str, appliance_type: Optional[str] = "any", limit: int = 5
    ) -> Dict[str, Any]:
        query_clean = query.strip().upper()
        db = SessionLocal()

        try:
            # ---------------------------------------------------------
            # 1. EXACT MATCH (best for part numbers)
            # ---------------------------------------------------------
            if PART_NUMBER_PATTERN.match(query_clean):
                exact_product = (
                    db.query(Product).filter(Product.part_number == query_clean).first()
                )

                if exact_product:
                    logger.info(f"[ProductSearch] Exact DB match for {query_clean}")

                    return {
                        "success": True,
                        "products": [
                            {
                                "part_number": exact_product.part_number,
                                "name": exact_product.name,
                                "description": exact_product.description,
                                "price": exact_product.price,
                                "image_url": exact_product.image_url,
                                "category": exact_product.category,
                                "appliance_type": exact_product.appliance_type,
                                "in_stock": exact_product.in_stock,
                                "relevance_score": 1.0,  # perfect match
                            }
                        ],
                        "count": 1,
                    }

            # ---------------------------------------------------------
            # 2. SQL FUZZY FALLBACK (name/desc/partial match)
            # ---------------------------------------------------------
            fuzzy_products = (
                db.query(Product)
                .filter(
                    or_(
                        Product.part_number.ilike(f"%{query_clean}%"),
                        Product.name.ilike(f"%{query_clean}%"),
                        Product.description.ilike(f"%{query_clean}%"),
                    )
                )
                .limit(limit)
                .all()
            )

            if fuzzy_products:
                logger.info(f"[ProductSearch] Fuzzy SQL match for {query_clean}")

                products = [
                    {
                        "part_number": p.part_number,
                        "name": p.name,
                        "description": p.description,
                        "price": p.price,
                        "image_url": p.image_url,
                        "category": p.category,
                        "appliance_type": p.appliance_type,
                        "in_stock": p.in_stock,
                        "relevance_score": 0.8,
                    }
                    for p in fuzzy_products
                ]

                return {"success": True, "products": products, "count": len(products)}

            # ---------------------------------------------------------
            # 3. VECTOR SEARCH (semantic match, last resort)
            # ---------------------------------------------------------
            vector_store = get_vector_store()
            results = vector_store.search_products(query_clean, n_results=limit)

            if not results:
                logger.warning(f"[ProductSearch] No match at all for {query_clean}")
                return {
                    "success": True,
                    "products": [],
                    "message": "No products found matching your query",
                }

            # Rehydrate full product info
            products = []
            for result in results:
                part_number = result.get("part_number")
                p = db.query(Product).filter(Product.part_number == part_number).first()

                if p:
                    products.append(
                        {
                            "part_number": p.part_number,
                            "name": p.name,
                            "description": p.description,
                            "price": p.price,
                            "image_url": p.image_url,
                            "category": p.category,
                            "appliance_type": p.appliance_type,
                            "in_stock": p.in_stock,
                            "relevance_score": result.get("relevance_score", 0),
                        }
                    )

            logger.info(
                f"[ProductSearch] Vector results for '{query_clean}': {len(products)} products"
            )

            return {"success": True, "products": products, "count": len(products)}

        except Exception as e:
            logger.error(f"Error in product search: {e}", exc_info=True)
            return {"success": False, "error": str(e), "products": []}

        finally:
            db.close()
