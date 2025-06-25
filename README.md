# Tavily Agent

A [LangGraph](https://langchain-ai.github.io/langgraph/) agent that implements the [Agent2Agent (A2A) Protocol](https://google-a2a.github.io/A2A/) with access to the [Tavily Search API](https://www.tavily.com/).

This repository was created for the [Agent2Agent (A2A) UI](https://github.com/A2ANet/A2AUI).

## Installation & Usage

### Local A2A Server

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

### Docker A2A Server

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

## Deployment

You can deploy the containerised agent to various cloud platforms.

### Google Cloud Run

To deploy the agent (and set up continuous deployment) with Google Cloud Run:

1. Fork the repository
2. Go to https://cloud.google.com/
3. Create or select a project
4. Search for "Cloud Run"
5. Click "Connect repo"
6. Select "Continuously deploy from a repository (source or function)"
7. Click "Set up with Cloud Build"
8. Select the forked repository > click "Next"
9. Select "Dockerfile" > click "Save"
10. Untick "Use IAM to authenticate incoming requests"
11. Copy the "Endpoint URL"
12. Open "Containers, Volumes, Networking, Security" > "Variables & Secrets" > click "Add variable"
13. Set "Name 1" to "SERVICE_URL" and "Value 1" to the copied "Endpoint URL"
14. Under "Secrets exposed as environment variables" click "Reference a secret"
15. Set "Name 1" to "ANTHROPIC_API_KEY"
16. Click "Secret" > "Create new secret"
17. Set "Name" to "ANTHROPIC_API_KEY" and "Secret value" to your Anthropic API key > click "Create Secret"
18. Set "Version 1" to "latest"
19. Under "Secrets exposed as environment variables" click "Reference a secret"
20. Set "Name 1" to "TAVILY_API_KEY"
21. Click "Secret" > "Create new secret"
22. Set "Name" to "TAVILY_API_KEY" and "Secret value" to your Tavily API key > click "Create Secret"
23. Set "Version 1" to "latest"
24. Click "Done"
25. Click "Create"
26. In the error message copy the revision service account (e.g. "XXXXXXXXXXXX-compute@developer.gserviceaccount.com)
27. Search for "Secret Manager"
28. Select "ANTHROPIC_API_KEY" and "TAVILY_API_KEY"
29. Click "ADD PRINCIPAL"
30. Set "New principals" to the revision service account (e.g. "XXXXXXXXXXXX-compute@developer.gserviceaccount.com)
31. Click "Select a role" and search for "Secret Manager Secret Accessor"
32. Click "Save"
33. Search for "Cloud Run"
34. Click "Edit & deploy new revision" > Click "Deploy"

The agent should be deployed. To check it's been deployed successfully:

**Retrieve the Agent Card**

1. Copy the "URL"
2. Open a new tab and paste the URL
3. Add ".well-known/agent.json" to the end of it (e.g. https://tavilyagent-XXXXXXXXXXXX.region.run.app/.well-known/agent.json)
4. Press <ENTER>, you should be able to see an agent card!

**Connect with the A2A UI**

1. Set up the [Agent2Agent (A2A) UI](https://github.com/A2ANet/A2AUI)
2. Go to http://localhost:3000
3. Click "+ Agent"
4. Paste the URL (e.g. https://tavilyagent-XXXXXXXXXXXX.region.run.app)
5. Send a message to the Tavily Agent, you should get a response!

The agent has been successfully deployed and will automatically redeploy when changes are pushed to the repo!
