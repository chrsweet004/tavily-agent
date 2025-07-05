import json
import uuid

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import (
    DataPart,
    Message,
    Role,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils import new_agent_text_message, new_task, new_text_artifact
from loguru import logger

from agent import TavilyAgent


class TavilyAgentExecutor(AgentExecutor):
    def __init__(self) -> None:
        self.agent: TavilyAgent = TavilyAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query: str = context.get_user_input()
        task: Task | None = context.current_task

        if not context.message:
            raise Exception("No message in context")

        if not task:
            task = new_task(context.message)
            event_queue.enqueue_event(task)

        async for event in self.agent.stream(query, task.contextId):
            logger.info(f"Event: {json.dumps(event, indent=4)}")

            if event["type"] == "message":
                event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=TaskState.working,
                            message=new_agent_text_message(
                                event["content"], task.contextId, task.id
                            ),
                        ),
                        final=False,
                        contextId=task.contextId,
                        taskId=task.id,
                    )
                )
            elif event["type"] == "tool_call":
                event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=TaskState.working,
                            message=Message(
                                contextId=task.contextId,
                                messageId=str(uuid.uuid4()),
                                parts=[DataPart(data=event["tool_call_args"])],
                                metadata={
                                    "type": "tool-call",
                                    "toolCallId": event["tool_call_id"],
                                    "toolCallName": event["tool_call_name"],
                                },
                                role=Role.agent,
                                taskId=task.id,
                            )
                        ),
                        final=False,
                        contextId=task.contextId,
                        taskId=task.id,
                    )
                )
            elif event["type"] == "tool_call_result":
                event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=TaskState.working,
                            message=Message(
                                contextId=task.contextId,
                                messageId=str(uuid.uuid4()),
                                parts=[DataPart(data=event["tool_call_result"])],
                                metadata={
                                    "type": "tool-call-result",
                                    "toolCallId": event["tool_call_id"],
                                    "toolCallName": event["tool_call_name"],
                                },
                                role=Role.agent,
                                taskId=task.id,
                            )
                        ),
                        final=False,
                        contextId=task.contextId,
                        taskId=task.id,
                    )
                )
            elif event["type"] == "response" and event["require_user_input"]:
                event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(
                            state=TaskState.input_required,
                        ),
                        final=True,
                        contextId=task.contextId,
                        taskId=task.id,
                    )
                )
            elif event["type"] == "response" and event["is_task_complete"]:
                event_queue.enqueue_event(
                    TaskArtifactUpdateEvent(
                        artifact=new_text_artifact(
                            name="Tavily Search Result",
                            description=event["task_description"],
                            text=event["task_output"],
                        ),
                        contextId=task.contextId,
                        taskId=task.id,
                    )
                )

                event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        status=TaskStatus(state=TaskState.completed),
                        final=True,
                        contextId=task.contextId,
                        taskId=task.id,
                    )
                )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("Cancel not supported")
