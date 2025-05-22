# ai-agents-service-usage

"""
Example: Using Azure AI Agents Service to generate a code style guide

This snippet demonstrates how to use the Azure AI Agents service (via the `azure.ai.projects.aio` SDK) to orchestrate an agent that generates a Markdown code style guide by leveraging a vector search tool for code examples. It covers agent creation, tool registration, thread/message management, and run monitoring.
"""
import os
import logging
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import AsyncFunctionTool
from azure.identity.aio import DefaultAzureCredential
from agents.tools import vector_search

logger = logging.getLogger(__name__)
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("azure.core").setLevel(logging.WARNING)
logging.getLogger("azure.ai.projects").setLevel(logging.WARNING)

_CODE_STYLE_SYSTEM_PROMPT = """
You are CodeStyleSynthesizer, an autonomous agent that produces a code style guide.

You have access to a vector_search tool that can find relevant code snippets in the database.

Your task is to:
1. Perform a SINGLE vector search to find relevant code snippets that demonstrate various coding patterns
2. Analyze ALL patterns and conventions found in the code
3. Generate a comprehensive code style guide in Markdown format

The style guide should cover:
- Naming conventions
- Code organization
- Documentation standards
- Error handling
- Logging practices
- Any other relevant style aspects

For each section, provide:
- Clear, concise rules
- Examples from actual code snippets
- Best practices and recommendations

IMPORTANT: Use vector_search only ONCE to get a comprehensive set of examples. Do not make multiple searches.

Return only the final Markdown document, no additional commentary.
"""

async def generate_code_style(chat_history: str = "", user_query: str = "") -> str:
    """Generates a code style guide using an AI agent."""
    try:
        logger.info("Starting code style generation with:")
        logger.info("Chat history length: %d characters", len(chat_history))
        if chat_history:
            logger.info("Chat history preview: %s", chat_history[:200] + "..." if len(chat_history) > 200 else chat_history)
        logger.info("User query: %s", user_query)
        logger.info("System prompt:\n%s", _CODE_STYLE_SYSTEM_PROMPT)
        logger.info("Initializing Azure authentication")
        async with DefaultAzureCredential() as credential:
            logger.info("Connecting to Azure AI Project")
            async with AIProjectClient.from_connection_string(
                credential=credential,
                conn_str=os.environ["PROJECT_CONNECTION_STRING"]
            ) as project_client:
                logger.info("Setting up vector search tool")
                functions = AsyncFunctionTool(functions=[vector_search.vector_search])
                logger.info("Creating CodeStyleSynthesizer agent with model: %s", os.environ["AGENTS_MODEL_DEPLOYMENT_NAME"])
                agent = await project_client.agents.create_agent(
                    name="CodeStyleSynthesizer",
                    description="An agent that produces code style guides",
                    instructions=_CODE_STYLE_SYSTEM_PROMPT,
                    tools=functions.definitions,
                    model=os.environ["AGENTS_MODEL_DEPLOYMENT_NAME"]
                )
                logger.info("Created agent: %s with tool: vector_search", agent.name)
                logger.info("Creating conversation thread")
                thread = await project_client.agents.create_thread()
                if chat_history:
                    logger.info("Adding chat history to thread")
                    await project_client.agents.create_message(
                        thread_id=thread.id,
                        role="user",
                        content=chat_history
                    )
                final_query = user_query if user_query else "Generate a code style guide."
                logger.info("Adding user query to thread: %s", final_query)
                await project_client.agents.create_message(
                    thread_id=thread.id,
                    role="user",
                    content=final_query
                )
                logger.info("Starting agent execution")
                run = await project_client.agents.create_run(
                    thread_id=thread.id,
                    agent_id=agent.id
                )
                tool_call_count = 0
                while True:
                    run = await project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
                    logger.info("Agent run status: %s", run.status)
                    if run.status == "completed":
                        logger.info("Agent run completed successfully")
                        break
                    elif run.status == "failed":
                        logger.error("Agent run failed with : %s", run)
                        raise Exception("Agent run failed")
                    elif run.status == "requires_action":
                        tool_calls = run.required_action.submit_tool_outputs.tool_calls
                        logger.info("Agent requires action with %d tool calls", len(tool_calls))
                        tool_outputs = []
                        for tool_call in tool_calls:
                            logger.info("Agent %s calling tool: %s with arguments: %s", 
                                      agent.name, 
                                      tool_call.function.name,
                                      tool_call.function.arguments)
                            output = await functions.execute(tool_call)
                            logger.info("Tool call completed with output length: %d", len(str(output)))
                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": output
                            })
                            tool_call_count += 1
                        await project_client.agents.submit_tool_outputs_to_run(
                            thread_id=thread.id,
                            run_id=run.id,
                            tool_outputs=tool_outputs
                        )
                logger.info("Retrieving final response from agent")
                messages = await project_client.agents.list_messages(thread_id=thread.id)
                response = str(messages.data[0].content[0].text.value)
                logger.info("Code style guide generated by %s (%d tool calls). Response length: %d", 
                          agent.name, tool_call_count, len(response))
                return response
    except Exception as e:
        logger.error("Code style generation failed with error: %s", str(e), exc_info=True)
        raise
