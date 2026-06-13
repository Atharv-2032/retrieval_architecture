from hybrid.run_hybrid import run_hybrid_query
from vector.run_vector import run_vector_query
from graph.run_graph import run_graph_query

def run():
    query = input("You:")
    print("vector:",run_vector_query(query))
    print("graph:",run_graph_query(query))
    print("hybrid:",run_hybrid_query(query))

if __name__ == "__main__":
    run()