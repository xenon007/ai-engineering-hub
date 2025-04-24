import asyncio
from mcp.server.fastmcp import FastMCP
from agents import run_research

# Create FastMCP instance
mcp = FastMCP("crew_research")


@mcp.tool()
async def crew_research(query: str) -> str:
    """Run CrewAI-based research system for given user query. Also does deep web search.

    Args:
        query (str): The research query or question.

    Returns:
        str: The research response from the CrewAI pipeline.
    """
    return run_research(query)


# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")


# I found the below format to work for a user on Cursor Discussion Forum, but did not work for me

# inside ./.cursor/mcp.json
# {
#     "mcpServers": {
#         "crew_research": {
#             "command": "C:\\Windows\\System32\\cmd.exe",
#             "args": [
#                 "/c",
#                 "python",
#                 "absolute path"
#             ],
#             "env": {
#                 "OPENROUTER_API_KEY": "key",
#                 "LINKUP_API_KEY": "key"
#             }
#         }
#     }
# }
