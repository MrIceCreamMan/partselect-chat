from typing import List
import re


class GuardRails:
    """Guard rails for keeping agent on topic"""

    # Keywords that indicate in-scope queries
    IN_SCOPE_KEYWORDS = [
        "refrigerator",
        "fridge",
        "freezer",
        "dishwasher",
        "ice maker",
        "water filter",
        "compressor",
        "spray arm",
        "pump",
        "rack",
        "part",
        "install",
        "replace",
        "fix",
        "repair",
        "model number",
        "compatible",
        "compatibility",
    ]

    # Keywords that indicate out-of-scope queries
    OUT_OF_SCOPE_KEYWORDS = [
        "oven",
        "stove",
        "range",
        "washer",
        "dryer",
        "laundry",
        "microwave",
        "weather",
        "news",
        "stock",
        "politics",
    ]

    @staticmethod
    def is_part_number(text: str) -> bool:
        """Check if text contains a part number pattern"""
        # Common part number patterns
        patterns = [
            r"[A-Z]{2}\d{8}",  # PS11752778
            r"\d{3,}-\d{3,}",  # 123-456
            r"[A-Z]\d{6,}",  # W10190965
        ]

        for pattern in patterns:
            if re.search(pattern, text.upper()):
                return True
        return False

    @staticmethod
    def is_model_number(text: str) -> bool:
        """Check if text contains a model number pattern"""
        # Common model number patterns
        patterns = [
            r"[A-Z]{3}\d{6}[A-Z]\d",  # WDT780SAEM1
            r"[A-Z]{2,}\d{3,}",  # GE123456
        ]

        for pattern in patterns:
            if re.search(pattern, text.upper()):
                return True
        return False

    @classmethod
    def quick_scope_check(cls, message: str) -> bool:
        """
        Quick keyword-based scope check before LLM call
        Returns True if likely in scope
        """
        message_lower = message.lower()

        # If it contains part/model numbers, likely in scope
        if cls.is_part_number(message) or cls.is_model_number(message):
            return True

        # Check for in-scope keywords
        in_scope_matches = sum(
            1 for keyword in cls.IN_SCOPE_KEYWORDS if keyword in message_lower
        )

        # Check for out-of-scope keywords
        out_scope_matches = sum(
            1 for keyword in cls.OUT_OF_SCOPE_KEYWORDS if keyword in message_lower
        )

        # If strong out-of-scope indicators, return False
        if out_scope_matches > 0 and in_scope_matches == 0:
            return False

        # If strong in-scope indicators, return True
        if in_scope_matches > 0:
            return True

        # Default to True for ambiguous cases (let LLM decide)
        return True
