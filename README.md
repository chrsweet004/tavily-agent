# Tavily Agent

A [LangGraph](https://langchain-ai.github.io/langgraph/) agent that implements the [Agent2Agent (A2A) Protocol](https://google-a2a.github.io/A2A/) with access to the [Tavily Search API](https://www.tavily.com/).

This repository was created for the [Agent2Agent (A2A) UI](https://github.com/A2ANet/A2AUI).

## Installation & Usage

### A2A Server

To use the Tavily Agent with A2A:

1. Clone the repository: `git clone https://github.com/A2ANet/TavilyAgent.git`
2. Create an `.env` file from `.env.example`
3. Set `ANTHROPIC_API_KEY` and `TAVILY_API_KEY`
4. Optionally, set `LANGSMITH_*` for LangSmith tracing
5. Install [uv](https://docs.astral.sh/uv/)
6. Run the A2A server: `uv run --env-file .env main.py`

The server will start on `http://localhost:9999`

### LangGraph Dev

To use the Tavily Agent with LangGraph:

1. Clone the repository: `git clone https://github.com/A2ANet/TavilyAgent.git`
2. Create an `.env` file from `.env.example`
3. Set `ANTHROPIC_API_KEY` and `TAVILY_API_KEY`
4. Optionally, set `LANGSMITH_*` for LangSmith tracing
5. Install the [LangGraph CLI](https://langchain-ai.github.io/langgraph/)
6. Run the agent: `langgraph dev`

### Docker

To run the agent using Docker:

1. Clone the repository: `git clone https://github.com/A2ANet/TavilyAgent.git`
2. Build the Docker image: `docker build -t tavily-agent .`
3. Run the container, providing your API keys as environment variables:

   ```bash
   docker run --rm -p 9999:9999 \
     -e TAVILY_API_KEY='your_tavily_api_key' \
     -e ANTHROPIC_API_KEY='your_anthropic_api_key' \
     tavily-agent
   ```

The server will start on `http://localhost:9999`
