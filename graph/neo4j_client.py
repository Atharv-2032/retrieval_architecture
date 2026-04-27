from neo4j import GraphDatabase
import os

class Neo4jClient:
    def __init__(self):
        password = os.getenv("NEO4J_PASS")
        url = os.getenv("NEO4J_URL")
        self.driver = GraphDatabase.driver(
            url,   
            auth=("neo4j",password )
        )

    def close(self):
        self.driver.close()

    def run_query(self, query, params=None):
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]







