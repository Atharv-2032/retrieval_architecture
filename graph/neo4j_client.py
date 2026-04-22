from neo4j import GraphDatabase


class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://172.21.16.1:7687",   
            auth=("neo4j", "Worldchampion") 
        )

    def close(self):
        self.driver.close()

    def run_query(self, query, params=None):
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]







