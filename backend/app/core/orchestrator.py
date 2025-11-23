from typing import List, Dict, Any, AsyncGenerator
import json
import logging
import re
from uuid import uuid4

from app.core.deepseek_client import get_deepseek_client
from app.core.prompts import SYSTEM_PROMPT, GUARD_RAIL_PROMPT, OUT_OF_SCOPE_RESPONSE
from app.tools.product_search import ProductSearchTool
from app.tools.compatibility import CompatibilityTool
from app.tools.troubleshooting import TroubleshootingTool
from app.models.schemas import ChatMessage, ChatResponse, StreamChunk
from config import settings

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self):
        self.deepseek = get_deepseek_client()

        # Initialize tools
        self.tools = {
            "product_search": ProductSearchTool(),
            "check_compatibility": CompatibilityTool(),
            "troubleshoot": TroubleshootingTool(),
        }

        # Tool definitions for Deepseek function calling
        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "product_search",
                    "description": "Search for refrigerator or dishwasher parts by name, part number, description, or problem. Returns relevant products with details.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g., 'ice maker', 'water filter', 'PS11752778')",
                            },
                            "appliance_type": {
                                "type": "string",
                                "enum": ["refrigerator", "dishwasher", "any"],
                                "description": "Type of appliance to filter by",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 5)",
                            },
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "check_compatibility",
                    "description": "Check if a specific part is compatible with a given appliance model number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "part_number": {
                                "type": "string",
                                "description": "The part number to check (e.g., 'PS11752778')",
                            },
                            "model_number": {
                                "type": "string",
                                "description": "The appliance model number (e.g., 'WDT780SAEM1')",
                            },
                        },
                        "required": ["part_number", "model_number"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "troubleshoot",
                    "description": "Diagnose appliance problems and get troubleshooting guidance with relevant parts suggestions",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "problem": {
                                "type": "string",
                                "description": "Description of the problem (e.g., 'ice maker not working', 'dishwasher not draining')",
                            },
                            "appliance_type": {
                                "type": "string",
                                "enum": ["refrigerator", "dishwasher"],
                                "description": "Type of appliance",
                            },
                            "brand": {
                                "type": "string",
                                "description": "Brand name (optional, e.g., 'Whirlpool', 'GE')",
                            },
                        },
                        "required": ["problem", "appliance_type"],
                    },
                },
            },
        ]

    async def check_scope(self, message: str) -> bool:
        """Check if message is within scope using LLM"""
        try:
            prompt = GUARD_RAIL_PROMPT.format(message=message)
            response = await self.deepseek.simple_completion(prompt)
            return "IN_SCOPE" in response.upper()
        except Exception as e:
            logger.error(f"Error in scope check: {e}")
            # Fail open - assume in scope if check fails
            return True

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool and return results"""
        try:
            tool = self.tools.get(tool_name)
            if not tool:
                return {"error": f"Tool {tool_name} not found"}

            result = await tool.execute(**arguments)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}

    async def process_message(
        self, message: str, conversation_history: List[ChatMessage]
    ) -> ChatResponse:
        """Process a message through the orchestrator"""

        # Check scope
        is_in_scope = await self.check_scope(message)
        if not is_in_scope:
            return ChatResponse(
                message=OUT_OF_SCOPE_RESPONSE,
                conversation_id=str(uuid4()),
                metadata={"out_of_scope": True},
            )

        # Build messages for Deepseek
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history
        for msg in conversation_history[-5:]:  # Keep last 5 messages for context
            messages.append({"role": msg.role, "content": msg.content})

        # Add current message
        messages.append({"role": "user", "content": message})

        # First LLM call with tools
        response = await self.deepseek.chat_completion(
            messages=messages, tools=self.tool_definitions
        )

        assistant_message = response["choices"][0]["message"]

        # DEBUG: Log the response structure
        logger.info(f"Assistant message keys: {assistant_message.keys()}")
        logger.info(f"Content: {assistant_message.get('content', 'None')[:200]}")
        logger.info(f"Tool calls: {assistant_message.get('tool_calls', 'None')}")

        # Check if tools were called
        tool_calls = assistant_message.get("tool_calls", [])

        # If content contains tool syntax but no tool_calls, it's a formatting issue
        content = assistant_message.get("content", "")
        if "tool_call" in content.lower() and not tool_calls:
            logger.error("Tool syntax found in content but no tool_calls structure!")

        if not tool_calls:
            # No tools needed, return response directly
            return ChatResponse(
                message=assistant_message.get("content", ""),
                conversation_id=str(uuid4()),
            )

        # Execute tools
        messages.append(assistant_message)

        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])

            logger.info(f"Executing tool: {function_name} with args: {function_args}")

            # Execute tool
            tool_result = await self.execute_tool(function_name, function_args)

            # Add tool result to messages
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": function_name,
                    "content": json.dumps(tool_result),
                }
            )

        # Second LLM call with tool results
        final_response = await self.deepseek.chat_completion(messages=messages)
        final_message = final_response["choices"][0]["message"]["content"]

        # Extract products from tool results
        products = []
        compatibility = None

        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])
            tool_result = await self.execute_tool(function_name, function_args)

            if function_name == "product_search" and "products" in tool_result:
                products.extend(tool_result["products"])
            elif function_name == "check_compatibility" and "compatible" in tool_result:
                compatibility = tool_result

        return ChatResponse(
            message=final_message,
            conversation_id=str(uuid4()),
            products=products[:5] if products else None,  # Limit to top 5
            compatibility=compatibility,
        )

    async def stream_message(
        self, message: str, conversation_history: List[ChatMessage]
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream response with tool execution"""

        # Check scope first
        is_in_scope = await self.check_scope(message)
        if not is_in_scope:
            yield StreamChunk(type="text", content=OUT_OF_SCOPE_RESPONSE)
            yield StreamChunk(type="done", content=None)
            return

        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        for msg in conversation_history[-5:]:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": message})

        # First call to get tool decisions (non-streaming)
        response = await self.deepseek.chat_completion(
            messages=messages, tools=self.tool_definitions
        )

        assistant_message = response["choices"][0]["message"]
        tool_calls = assistant_message.get("tool_calls", [])

        if tool_calls:
            # Execute tools and emit progress
            yield StreamChunk(
                type="thinking", content="Searching for that information..."
            )

            # DON'T YIELD THE FIRST RESPONSE - it contains tool syntax
            messages.append(assistant_message)

            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])

                # Execute tool
                tool_result = await self.execute_tool(function_name, function_args)

                # Emit tool results
                if function_name == "product_search" and "products" in tool_result:
                    for product in tool_result["products"][:5]:
                        yield StreamChunk(type="product", content=product)

                elif function_name == "check_compatibility":
                    yield StreamChunk(type="compatibility", content=tool_result)

                # Add to messages
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": function_name,
                        "content": json.dumps(tool_result),
                    }
                )

            async for chunk in self.deepseek.stream_chat_completion(messages=messages):
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta and delta["content"]:
                        yield StreamChunk(type="text", content=delta["content"])
        else:
            # No tools, stream directly
            async for chunk in self.deepseek.stream_chat_completion(messages=messages):
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta and delta["content"]:
                        yield StreamChunk(type="text", content=delta["content"])

        yield StreamChunk(type="done", content=None)


# Global instance
_orchestrator = None


def get_orchestrator() -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
