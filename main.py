import os

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from starlette.middleware.cors import CORSMiddleware

from agent_executor import TavilyAgentExecutor

skill = AgentSkill(
    id="search-web",
    name="Search Web",
    description="Search the web with the Tavily API and answer questions about the results.",
    tags=["search", "web", "tavily"],
    examples=["Who is Leo Messi?"],
)

# Get port from environment variable
port = int(os.getenv("PORT"))
# Get service URL for agent card (Cloud Run will provide this)
service_url = os.getenv("SERVICE_URL", f"http://localhost:{port}")

agent_card = AgentCard(
    name="Tavily Agent",
    description="Search the web with the Tavily API and answer questions about the results.",
    url=service_url,
    version="1.0.0",
    defaultInputModes=["text", "text/plain"],
    defaultOutputModes=["text", "text/plain"],
    capabilities=AgentCapabilities(),
    skills=[skill],
)

request_handler: DefaultRequestHandler = DefaultRequestHandler(
    agent_executor=TavilyAgentExecutor(), task_store=InMemoryTaskStore()
)

server: A2AStarletteApplication = A2AStarletteApplication(
    agent_card=agent_card, http_handler=request_handler
)

# Build the server and wrap it with CORS middleware so browsers can access it directly
app = server.build()

app = CORSMiddleware(
    app=app,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
