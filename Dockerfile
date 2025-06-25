# Use the official uv image with Python 3.13
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash appuser

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --locked --no-install-project

# Copy application code
COPY main.py ./
COPY agent.py ./
COPY agent_executor.py ./

# Sync the project (install the project itself)
RUN uv sync --locked

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port the app runs on (Cloud Run will set PORT environment variable)
EXPOSE $PORT

# Use uv to run the application with PORT environment variable
CMD ["sh", "-c", "uv run uvicorn main:app --host 0.0.0.0 --port $PORT"]
