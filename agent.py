import json
from collections.abc import AsyncIterable
from typing import Any, Dict, List, Literal, Set

from langchain_core.messages import AIMessage, AnyMessage, ToolMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.types import StateSnapshot
from loguru import logger
from pydantic import BaseModel

memory = MemorySaver()

tavily_search: TavilySearch = TavilySearch(max_results=2)


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal["completed", "input_required", "error"] = "input_required"
    task_description: str = ""
    task_output: str = ""


class TavilyAgent:
    """Tavily Agent that can search the web with the Tavily API and answer questions about the results."""

    SYSTEM_INSTRUCTION: str = (
        "You are a helpful assistant that can search the web with the Tavily API and answer questions about the results. "
        "If the `tavily_search` tool returns insufficient results, you should explain that to the user and ask them to try again with a more specific query. "
        "You can use markdown format to format your responses."
    )

    RESPONSE_FORMAT_INSTRUCTION: str = (
        "`status` should be 'completed' if the request is complete. "
        "The request is complete if the `tavily_search` tool has been called and the results are sufficient to answer the user's question. "
        "If `status` is 'completed', `task_description` should be the exact search query that was used to get the results and `task_output` should be the output of the task. "
        "`task_output` supports markdown format. "
        "`status` should be 'input_required' if input is required from the user. "
        "Input is required if the `tavily_search` tool has been called and the results are insufficient to answer the user's question. "
        "`status` should be 'error' if an error has occurred."
    )

    def __init__(self) -> None:
        self.graph = create_react_agent(
            model="anthropic:claude-sonnet-4-20250514",
            tools=[tavily_search],
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=(self.RESPONSE_FORMAT_INSTRUCTION, ResponseFormat),
        )

    async def stream(self, query: str, sessionId: str) -> AsyncIterable[dict[str, Any]]:
        inputs: Dict[str, Any] = {"messages": [("user", query)]}
        config: RunnableConfig = {"configurable": {"thread_id": sessionId}}
        message_ids: Set[str] = set()

        for event in self.graph.stream(inputs, config, stream_mode="values"):
            message: AnyMessage = event["messages"][-1]

            if message.id in message_ids:
                continue

            logger.info(f"Message: {message.model_dump_json(indent=4)}")
            message_ids.add(message.id)

            if isinstance(message, AIMessage):
                content: str | List[str | Dict] = message.content

                if isinstance(content, str):
                    yield {
                        "type": "message",
                        "content": content,
                    }
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, str):
                            yield {
                                "type": "message",
                                "content": content,
                            }
                        elif isinstance(item, dict) and item["type"] == "text":
                            yield {
                                "type": "message",
                                "content": item["text"],
                            }

                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        yield {
                            "type": "tool_call",
                            "tool_call_id": tool_call["id"],
                            "tool_call_name": tool_call["name"],
                            "tool_call_args": tool_call["args"],
                        }
            elif isinstance(message, ToolMessage):
                tool_call_result: str | List[str | Dict] = message.content

                try:
                    tool_call_result: str | Dict | List[str | Dict] = json.loads(tool_call_result)
                except json.JSONDecodeError:
                    continue

                yield {
                    "type": "tool_call_result",
                    "tool_call_id": message.tool_call_id,
                    "tool_call_name": message.name,
                    "tool_call_result": tool_call_result,
                }

        yield self.get_agent_response(config)

    def get_agent_response(self, config: RunnableConfig) -> Dict[str, Any]:
        current_state: StateSnapshot = self.graph.get_state(config)
        structured_response: ResponseFormat = current_state.values.get(
            "structured_response"
        )

        if structured_response and isinstance(structured_response, ResponseFormat):
            if structured_response.status in ["input_required", "error"]:
                return {
                    "type": "response",
                    "is_task_complete": False,
                    "require_user_input": True,
                }
            elif structured_response.status == "completed":
                return {
                    "type": "response",
                    "task_description": structured_response.task_description,
                    "task_output": structured_response.task_output,
                    "is_task_complete": True,
                    "require_user_input": False,
                }

        return {
            "type": "response",
            "is_task_complete": False,
            "require_user_input": True,
        }
