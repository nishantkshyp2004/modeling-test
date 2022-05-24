from nodes import GraphStructure, QueryFactory
from edge import Edge
import json

graph = GraphStructure("../request-data.json")
graph_dict = json.loads(graph.json)
print(graph_dict)

edge = Edge(graph_dict)
edge.evaluate_graph()
graph_order = edge.get_graph_order()
print(graph_order)

def run():
    #initialize query with None
    query=None
    node_query = {}
    #Creating Query factory instance.
    qf = QueryFactory()
    for node_name in graph_order:
        for node in graph_dict["nodes"]:
            if node["key"] == node_name:
                query = qf.get_query(node, graph_order, query=query)
                node_query[node_name] = query
                break
    #generate finaly sub query.
    # for node_name, query in node_query.items():
    #     final_query = (Query
    #                    .with_(query, node_name)
    #                    .AliasedQuery(node_name)
    #                    )
    print(query)
    with open('result_withclause.sql', 'w') as file:
        file.write(query.get_sql())

if __name__ == '__main__':
    run()

