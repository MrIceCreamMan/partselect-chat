from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timezone


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    conversation_history: List[ChatMessage] = Field(default_factory=list)


class ProductInfo(BaseModel):
    part_number: str
    name: str
    description: str
    price: float
    image_url: Optional[str] = None
    category: str
    appliance_type: str
    in_stock: bool = True


class CompatibilityResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    compatible: bool
    part_number: str
    model_number: str
    confidence: float
    explanation: str


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None


class ChatResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    message: str
    conversation_id: str
    products: Optional[List[ProductInfo]] = None
    compatibility: Optional[CompatibilityResult] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StreamChunk(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    type: Literal["text", "product", "compatibility", "thinking", "done", "error"]
    content: Any
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
