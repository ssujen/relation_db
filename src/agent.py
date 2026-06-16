import os
import sys

# Add project root to system path to resolve imports correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
import asyncio
from dotenv import load_dotenv
from google.antigravity import Agent, LocalAgentConfig
from src.database import db_manager

# Load environment variables
load_dotenv()

# Map GOOGLE_API_KEY to GEMINI_API_KEY if needed (Google Antigravity SDK expects GEMINI_API_KEY)
if "GOOGLE_API_KEY" in os.environ and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

MODEL_NAME = os.getenv("MODEL", "gemini-3.5-flash")

def run_cypher_query(query: str) -> str:
    """Executes a Cypher query on the FalkorDB database and returns the result as a string.
    Use this tool to search, read, or count nodes and relationships in the graph.

    Args:
        query: The OpenCypher query string to execute. Example: "MATCH (p:Person) RETURN p.name, p.location"
    """
    try:
        result = db_manager.execute_query(query)
        if not result.result_set:
            return "Query completed. No results found."
        
        # Format output
        rows = []
        for record in result.result_set:
            rows.append(", ".join(str(val) for val in record))
        return "\n".join(rows)
    except Exception as e:
        return f"Error executing Cypher query: {str(e)}"

# System instruction guiding the model on FalkorDB relationship queries
SYSTEM_INSTRUCTIONS = """
You are a graph database relationship assistant. Your job is to answer the user's questions about people and their relationships.
You have access to a FalkorDB database via the run_cypher_query tool.

Database Schema Info:
- Nodes: Label `Person` with properties `name` (unique identifier) and `location`.
- Relationships: Type `RELATES_TO` (directed from Person1 to Person2) with properties `type` (e.g., "friend", "husband", "enemy", "boss") and `sentiment` (e.g., "love", "like", "neutral", "dislike", "hate").

Instructions:
1. Translate the user's natural language question into one or more Cypher queries.
2. Execute the Cypher query using the `run_cypher_query` tool.
3. Formulate a friendly, concise natural language answer based on the database query results.
4. If the query returns "No results found" or an error, try an alternative query or report that no such relationships are recorded.
5. If the user asks you to add or modify data, remind them to use the Streamlit interface form instead, as your main role is querying.
"""

def get_agent_config() -> LocalAgentConfig:
    """
    Builds the agent configuration with the configured model and tools.
    """
    return LocalAgentConfig(
        model=MODEL_NAME,
        tools=[run_cypher_query],
        system_instructions=SYSTEM_INSTRUCTIONS
    )

async def ask_agent(query_text: str) -> str:
    """
    Asks the Antigravity agent a question and returns its text response.
    """
    config = get_agent_config()
    async with Agent(config=config) as agent:
        response = await agent.chat(query_text)
        return await response.text()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ask the Relationship AI Agent a query.")
    parser.add_argument("--query", type=str, required=True, help="Natural language query for the agent.")
    args = parser.parse_args()

    async def main():
        response_text = await ask_agent(args.query)
        print("\nAgent Response:")
        print(response_text)

    asyncio.run(main())
