from mcp.server.fastmcp import FastMCP
from agents import run_research

# Create FastMCP instance
mcp = FastMCP("crew_research", host="127.0.0.1", port=8080, timeout=30)


@mcp.tool()
def crew_research(query: str) -> str:
    """Run CrewAI-based research system for given user query. Also does deep web search.

    Args:
        query (str): The research query or question.

    Returns:
        str: The research response from the CrewAI pipeline.
    """
    return run_research(query)


# Run the server
if __name__ == "__main__":
    print("Starting Crew Research Wrapper...")
    mcp.run()


# As suggested by Avi Bhaiya

# {
#   "mcpServers": {
#     "crew_research": {
#       "command": "python",
#       "args": ["path"],
#       "host": "127.0.0.1",
#       "port": 8080,
#       "timeout": 30000,
#       "env": {
#         "OPENROUTER_API_KEY": "key",
#         "LINKUP_API_KEY": "key"
#       }
#     }
#   }
# }
