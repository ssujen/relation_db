import os
import sys

# Add project root to system path to resolve imports correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.database import db_manager

def test_database_operations():
    # Clear the graph to ensure clean test state
    db_manager.clear_graph()

    # 1. Upsert nodes
    db_manager.upsert_person("Alice", "New York")
    db_manager.upsert_person("Bob", "Los Angeles")

    # Verify nodes exist via custom query
    res_nodes = db_manager.execute_query("MATCH (p:Person) RETURN p.name, p.location")
    nodes = {row[0]: row[1] for row in res_nodes.result_set}
    
    assert "Alice" in nodes
    assert nodes["Alice"] == "New York"
    assert "Bob" in nodes
    assert nodes["Bob"] == "Los Angeles"

    # 2. Create relationship
    db_manager.create_relationship("Alice", "Bob", "friend", "love")

    # Verify relationship exists
    res_rel = db_manager.execute_query(
        "MATCH (p1:Person {name: 'Alice'})-[r:RELATES_TO]->(p2:Person {name: 'Bob'}) RETURN r.type, r.sentiment"
    )
    assert len(res_rel.result_set) == 1
    rel_type, sentiment = res_rel.result_set[0]
    assert rel_type == "friend"
    assert sentiment == "love"

    # 3. Clear graph
    db_manager.clear_graph()
    res_empty = db_manager.execute_query("MATCH (n) RETURN count(n)")
    assert res_empty.result_set[0][0] == 0
