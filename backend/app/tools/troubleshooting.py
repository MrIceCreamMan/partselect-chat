from typing import Dict, Any, Optional
import logging
from app.tools.base import BaseTool
from app.services.vector_store import get_vector_store
from app.tools.product_search import ProductSearchTool

logger = logging.getLogger(__name__)


class TroubleshootingTool(BaseTool):
    def __init__(self):
        self.product_search = ProductSearchTool()

    @property
    def name(self) -> str:
        return "troubleshoot"

    @property
    def description(self) -> str:
        return "Diagnose appliance problems and suggest solutions"

    async def execute(
        self, problem: str, appliance_type: str, brand: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Troubleshoot appliance issues
        """
        try:
            vector_store = get_vector_store()

            # Search troubleshooting knowledge base
            query = f"{appliance_type} {problem}"
            if brand:
                query = f"{brand} {query}"

            guides = vector_store.search_troubleshooting(query, n_results=2)

            # Also search for relevant parts
            parts_result = await self.product_search.execute(
                query=problem, appliance_type=appliance_type, limit=3
            )

            return {
                "success": True,
                "problem": problem,
                "appliance_type": appliance_type,
                "guides": guides,
                "suggested_parts": parts_result.get("products", []),
                "diagnostic_steps": self._generate_diagnostic_steps(
                    problem, appliance_type
                ),
            }

        except Exception as e:
            logger.error(f"Error in troubleshooting: {e}")
            return {"success": False, "error": str(e)}

    def _generate_diagnostic_steps(self, problem: str, appliance_type: str) -> list:
        """Generate basic diagnostic steps based on problem"""
        problem_lower = problem.lower()

        # Common diagnostic patterns
        if "ice maker" in problem_lower and appliance_type == "refrigerator":
            return [
                "Check if the ice maker is turned on (look for the power switch or bail arm)",
                "Verify water supply is connected and valve is open",
                "Check for frozen water line",
                "Listen for water filling sounds during ice making cycle",
                "Inspect ice maker assembly for visible damage",
            ]
        elif "not cooling" in problem_lower and appliance_type == "refrigerator":
            return [
                "Check if the refrigerator is plugged in and receiving power",
                "Verify temperature settings are correct",
                "Listen for compressor running",
                "Check if condenser coils are dirty (clean if needed)",
                "Ensure door seals are intact and closing properly",
            ]
        elif "not draining" in problem_lower and appliance_type == "dishwasher":
            return [
                "Check for clogs in the drain hose",
                "Inspect the drain pump for debris",
                "Verify the air gap (if present) is clear",
                "Check the garbage disposal connection",
                "Test the drain pump for proper operation",
            ]
        elif "not cleaning" in problem_lower and appliance_type == "dishwasher":
            return [
                "Check spray arms for clogs",
                "Verify water temperature is adequate (120°F minimum)",
                "Inspect water inlet valve",
                "Clean the filter at the bottom of the tub",
                "Check detergent dispenser operation",
            ]
        else:
            return [
                f"Verify the {appliance_type} is receiving power",
                "Check for any error codes on the display",
                "Inspect for visible damage or loose connections",
                "Review the owner's manual for specific troubleshooting steps",
                "Consider the age and maintenance history of the appliance",
            ]
