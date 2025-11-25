import os
from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from a2a.utils import new_agent_text_message

import apeiron.instrumentation


class ApeironAgentExecutor(AgentExecutor):
    def __init__(self):
        pass

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        await event_queue.enqueue_event(new_agent_text_message("Hello from Apeiron"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("cancel not supported")


def create_app():
    apeiron.instrumentation.init()
    host_override = os.getenv("HOST_OVERRIDE", "http://0.0.0.0:8000/")
    skill = AgentSkill(
        id="chat",
        name="Chat",
        description="General chat and assistance",
        tags=["chat", "assistant"],
        examples=["hello", "help"],
    )
    card = AgentCard(
        name="Apeiron Agent",
        description="Apeiron A2A-enabled agent",
        url=host_override,
        version="0.1.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
    )
    handler = DefaultRequestHandler(
        agent_executor=ApeironAgentExecutor(), task_store=InMemoryTaskStore()
    )
    server = A2AStarletteApplication(agent_card=card, http_handler=handler)
    return server.build()


# End of file
