from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json
import logging
from datetime import datetime, timezone

from app.models.schemas import ChatRequest, ChatResponse, ChatMessage, StreamChunk
from app.core.orchestrator import get_orchestrator
from app.services.database import get_db
from app.models.database_models import Conversation, Message
from uuid import uuid4

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a chat message and get response (non-streaming)
    """
    try:
        orchestrator = get_orchestrator()

        # Process message
        response = await orchestrator.process_message(
            message=request.message, conversation_history=request.conversation_history
        )

        # Store conversation in database
        conversation_id = request.conversation_id or str(uuid4())

        # Get or create conversation
        conversation = (
            db.query(Conversation)
            .filter(Conversation.conversation_id == conversation_id)
            .first()
        )

        if not conversation:
            conversation = Conversation(conversation_id=conversation_id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # Store user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(user_message)

        # Store assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response.message,
            message_metadata={
                "products": [p.dict() for p in response.products]
                if response.products
                else None,
                "compatibility": response.compatibility.dict()
                if response.compatibility
                else None,
            },
            timestamp=datetime.now(timezone.utc),
        )
        db.add(assistant_message)

        db.commit()

        # Update response with conversation ID
        response.conversation_id = conversation_id

        return response

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def stream_message(request: ChatRequest):
    """
    Stream chat response with Server-Sent Events
    """

    async def event_generator():
        try:
            orchestrator = get_orchestrator()

            async for chunk in orchestrator.stream_message(
                message=request.message,
                conversation_history=request.conversation_history,
            ):
                # Convert chunk to JSON and send as SSE
                chunk_data = chunk.model_dump(mode="json")
                # logger.error(f"data: {chunk_data}")
                yield f"data: {json.dumps(chunk_data)}\n\n"

        except Exception as e:
            error_chunk = StreamChunk(type="error", content={"error": str(e)})
            yield f"data: {json.dumps(error_chunk.dict())}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/chat/history/{conversation_id}")
async def get_conversation_history(conversation_id: str, db: Session = Depends(get_db)):
    """
    Get conversation history
    """
    try:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.conversation_id == conversation_id)
            .first()
        )

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.timestamp)
            .all()
        )

        return {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "message_metadata": msg.message_metadata,
                }
                for msg in messages
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/history/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    Delete a conversation and its messages
    """
    try:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.conversation_id == conversation_id)
            .first()
        )

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Delete messages
        db.query(Message).filter(Message.conversation_id == conversation.id).delete()

        # Delete conversation
        db.delete(conversation)
        db.commit()

        return {"message": "Conversation deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
