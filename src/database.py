import os
from dotenv import load_dotenv
from falkordb import FalkorDB

# Load environment variables
load_dotenv()

FALKORDB_HOST = os.getenv("FALKORDB_HOST", "localhost")
FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", "6379"))
GRAPH_NAME = os.getenv("GRAPH_NAME", "relationships_graph")

class DatabaseManager:
    def __init__(self):
        self.client = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
        self.graph = self.client.select_graph(GRAPH_NAME)

    def upsert_person(self, name: str, location: str):
        """
        Creates or updates a Person node with name and location.
        name is unique.
        """
        query = """
        MERGE (p:Person {name: $name})
        SET p.location = $location
        RETURN p
        """
        params = {"name": name, "location": location}
        return self.graph.query(query, params)

    def create_relationship(self, person1_name: str, person2_name: str, rel_type: str, sentiment: str):
        """
        Creates or updates a directed RELATES_TO edge from person1 to person2
        with type and sentiment properties.
        Assumes both Person nodes already exist or are merged.
        """
        # Ensure nodes exist
        self.graph.query("MERGE (p:Person {name: $name})", {"name": person1_name})
        self.graph.query("MERGE (p:Person {name: $name})", {"name": person2_name})

        query = """
        MATCH (p1:Person {name: $p1_name}), (p2:Person {name: $p2_name})
        MERGE (p1)-[r:RELATES_TO]->(p2)
        SET r.type = $type, r.sentiment = $sentiment
        RETURN r
        """
        params = {
            "p1_name": person1_name,
            "p2_name": person2_name,
            "type": rel_type,
            "sentiment": sentiment
        }
        return self.graph.query(query, params)

    def execute_query(self, query: str, params: dict = None):
        """
        Executes a Cypher query against the graph and returns the result.
        """
        return self.graph.query(query, params)

    def clear_graph(self):
        """
        Deletes all nodes and edges from the graph.
        """
        query = "MATCH (n) DETACH DELETE n"
        return self.graph.query(query)

# Global database manager instance
db_manager = DatabaseManager()
