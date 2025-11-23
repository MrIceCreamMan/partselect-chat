from typing import Dict, Any
import logging
from app.tools.base import BaseTool
from app.services.database import SessionLocal
from app.models.database_models import Product, Compatibility

logger = logging.getLogger(__name__)


class CompatibilityTool(BaseTool):
    @property
    def name(self) -> str:
        return "check_compatibility"

    @property
    def description(self) -> str:
        return "Check if a part is compatible with a specific model"

    async def execute(self, part_number: str, model_number: str) -> Dict[str, Any]:
        """
        Check compatibility between part and model
        """
        try:
            db = SessionLocal()

            try:
                # Find product
                product = (
                    db.query(Product).filter(Product.part_number == part_number).first()
                )

                if not product:
                    return {
                        "success": False,
                        "compatible": False,
                        "confidence": 0.0,
                        "explanation": f"Part number {part_number} not found in our database",
                    }

                # Check compatibility
                compatibility = (
                    db.query(Compatibility)
                    .filter(
                        Compatibility.product_id == product.id,
                        Compatibility.model_number == model_number.upper(),
                    )
                    .first()
                )

                if compatibility:
                    return {
                        "success": True,
                        "compatible": True,
                        "part_number": part_number,
                        "model_number": model_number,
                        "confidence": 1.0,
                        "explanation": f"Yes! Part {part_number} ({product.name}) is compatible with model {model_number}.",
                        "product": {
                            "name": product.name,
                            "price": product.price,
                            "image_url": product.image_url,
                        },
                    }
                else:
                    # Check if model exists for this product at all
                    any_compatibility = (
                        db.query(Compatibility)
                        .filter(Compatibility.product_id == product.id)
                        .first()
                    )

                    if any_compatibility:
                        explanation = f"Part {part_number} is not listed as compatible with model {model_number}. This part fits other models but not this specific one."
                    else:
                        explanation = f"We don't have compatibility information for part {part_number} with model {model_number}. Please verify with the manufacturer or contact support."

                    return {
                        "success": True,
                        "compatible": False,
                        "part_number": part_number,
                        "model_number": model_number,
                        "confidence": 0.8,
                        "explanation": explanation,
                        "product": {
                            "name": product.name,
                            "price": product.price,
                            "image_url": product.image_url,
                        },
                    }

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error checking compatibility: {e}")
            return {
                "success": False,
                "compatible": False,
                "confidence": 0.0,
                "explanation": f"Error checking compatibility: {str(e)}",
            }
