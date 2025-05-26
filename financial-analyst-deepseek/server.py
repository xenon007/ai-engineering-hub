from mcp.server.fastmcp import FastMCP
from finance_crew import run_financial_analysis

# create FastMCP instance
mcp = FastMCP("financial-analyst")

@mcp.tool()
def analyze_stock(query: str) -> str:
    """
    Analyzes the stock market data for the given query and write executable python code to analyze/visualize the data.
    Finally, save the code to a file stock_analysis.py and return a message to the user.
    The query is a string that must contain the stock symbol (e.g., TSLA, AAPL), 
    timeframe (e.g., 1d, 1mo, 1y), and action to perform (e.g., plot, analyze, compare).

    Example queries:
    - "Show me Tesla's stock performance over the last 3 months"
    - "Compare Apple and Microsoft stocks for the past year"
    - "Analyze the trading volume of Amazon stock for the last month"

    Args:
        query (str): The query to analyze the stock market data.
    
    Returns:
        str: A message to the user about the completion of the task.
    """
    try:
        result = run_financial_analysis(query)
        # Save the generated code to local directory
        with open('stock_analysis.py', 'w') as f:
            f.write(result.raw)
        return f"Stock analysis code saved to stock_analysis.py"
    except Exception as e:
        return f"Error: {e}"


# Run the server locally
if __name__ == "__main__":
    mcp.run(transport='stdio')