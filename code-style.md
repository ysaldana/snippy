# Project Code Style Guide

This code style guide is synthesized from the project's saved code snippets and best practices. It is intended to ensure consistency, readability, and maintainability across all Python code, with a focus on Azure Functions Python v2 and async Azure SDK usage.

---

## 1. Naming Conventions
- Use `snake_case` for variables, functions, and method names.
- Use `PascalCase` for class names.
- Constants should be `ALL_CAPS`.
- Environment variables must be referenced as `os.environ["NAME"]`.
- Function and variable names should be descriptive and concise.

**Example:**
```python
def generate_code_style(chat_history: str = "", user_query: str = "") -> str:
    ...
```

---

## 2. Code Organization
- Group imports by standard library, third-party, and local modules.
- Place all configuration and logging setup at the top of the file.
- Use docstrings for all public functions and classes (Google style, one-line summary).
- Keep function length manageable; break up long functions into logical units.
- Use async/await for all I/O and Azure SDK operations.

**Example:**
```python
import os
import logging
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from agents.tools import vector_search
```

---

## 3. Documentation Standards
- Every public function and class must have a docstring.
- Use Google-style docstrings with a one-line summary.
- Document all arguments and return values.

**Example:**
```python
def generate_code_style(chat_history: str = "", user_query: str = "") -> str:
    """Generates a code style guide using an AI agent."""
    ...
```

---

## 4. Error Handling
- Use try/except blocks for all major operations.
- Log errors with `logger.error` and include exception info (`exc_info=True`).
- Raise exceptions after logging for upstream handling.

**Example:**
```python
try:
    ...
except Exception as e:
    logger.error("Code style generation failed with error: %s", str(e), exc_info=True)
    raise
```

---

## 5. Logging Practices
- Use the `logging` module, not `print`.
- Set Azure SDK loggers to `WARNING` to reduce noise.
- Log all major steps at `INFO` level.
- Include context in log messages (e.g., agent name, tool call count).

**Example:**
```python
logger = logging.getLogger(__name__)
logging.getLogger("azure").setLevel(logging.WARNING)
logger.info("Starting code style generation with:")
```

---

## 6. Secrets and Configuration
- Never commit secrets or connection strings in code.
- Always access secrets and configuration via `os.environ`.
- Document required environment variables in code and documentation.

**Example:**
```python
conn_str=os.environ["PROJECT_CONNECTION_STRING"]
```

---

## 7. Async and Await
- Use async Azure SDKs (e.g., `AIProjectClient`, `DefaultAzureCredential`).
- Await only async methods; do not await synchronous APIs.
- Use `async def` for all functions that perform I/O or Azure SDK calls.

**Example:**
```python
async def generate_code_style(...):
    ...
    async with DefaultAzureCredential() as credential:
        ...
```

---

## 8. Tool and Agent Patterns (for Azure AI Agents)
- Register tools (e.g., `vector_search`) using `AsyncFunctionTool`.
- Create agents with clear instructions and tool definitions.
- Use a single vector search per agent run if required by the prompt.
- Manage agent threads, messages, and run lifecycle explicitly.
- Handle tool calls and submit outputs as required.

**Example:**
```python
functions = AsyncFunctionTool(functions=[vector_search.vector_search])
agent = await project_client.agents.create_agent(..., tools=functions.definitions, ...)
```

---

## 9. Environment Variables Required
- `PROJECT_CONNECTION_STRING`: Azure AI Project connection string
- `AGENTS_MODEL_DEPLOYMENT_NAME`: Model deployment name for the agent

---

## 10. General Best Practices
- Keep code modular and testable.
- Prefer explicit over implicit behavior.
- Use type hints throughout.
- Avoid global state except for configuration and logging.
- Follow Azure and Python best practices for security, error handling, and performance.

---

*This guide will evolve as new patterns and requirements emerge in the project.*
