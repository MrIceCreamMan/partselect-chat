import re
from typing import Optional, Dict, Any
import hashlib


def extract_part_number(text: str) -> Optional[str]:
    """Extract part number from text"""
    patterns = [r"(PS\d{8})", r"([A-Z]\d{8})", r"(\d{3,}-\d{3,})"]

    for pattern in patterns:
        match = re.search(pattern, text.upper())
        if match:
            return match.group(1)

    return None


def extract_model_number(text: str) -> Optional[str]:
    """Extract model number from text"""
    patterns = [r"([A-Z]{3}\d{6}[A-Z]\d)", r"([A-Z]{2,}\d{3,}[A-Z]?\d*)"]

    for pattern in patterns:
        match = re.search(pattern, text.upper())
        if match:
            return match.group(1)

    return None


def format_price(price: float) -> str:
    """Format price as currency"""
    return f"${price:.2f}"


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def generate_conversation_id(user_id: Optional[str] = None) -> str:
    """Generate a unique conversation ID"""
    import uuid
    import time

    if user_id:
        # Hash user_id with timestamp for uniqueness
        data = f"{user_id}_{time.time()}"
        return hashlib.md5(data.encode()).hexdigest()
    else:
        return str(uuid.uuid4())


def clean_html(text: str) -> str:
    """Remove HTML tags from text"""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def normalize_model_number(model: str) -> str:
    """Normalize model number for comparison"""
    # Remove spaces, hyphens, and convert to uppercase
    return re.sub(r"[\s\-]", "", model.upper())
