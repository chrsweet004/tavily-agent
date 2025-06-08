# Tavily Agent

A [LangGraph](https://langchain-ai.github.io/langgraph/) agent that implements the [Agent2Agent (A2A) Protocol](https://google-a2a.github.io/A2A/) with access to the [Tavily Search API](https://www.tavily.com/).

This repository was created for the [Agent2Agent (A2A) UI](https://github.com/A2ANet/A2AUI).

## Installation & Usage

To use the Tavily Agent with A2A and LangGraph:

1. Clone the repository: `git clone https://github.com/A2ANet/TavilyAgent.git`
2. Create an `.env` file from `.env.example`
3. Set `ANTHROPIC_API_KEY` and `TAVILY_API_KEY`
4. Optionally, set `LANGSMITH_*` for LangSmith tracing

### A2A Server

To use the Tavily Agent with A2A:

1. Install [uv](https://docs.astral.sh/uv/)
2. Run the A2A server: `uv run --env-file .env main.py`

The server will start on `http://localhost:9999`.

### LangGraph Dev

To use the Tavily Agent with LangGraph: 

1. Install the [LangGraph CLI](https://langchain-ai.github.io/langgraph/)
2. Run the agent: `langgraph dev`
