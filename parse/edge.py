from graphlib import TopologicalSorter

class Edge:

    def __init__(self, graph_json):
        self.graph_json = graph_json

    def evaluate_graph(self):
        start_nodes = list(map(lambda x: x["from"], self.graph_json["edges"]))
        end_nodes = list(map(lambda x: x["to"], self.graph_json["edges"]))
        self.graph = dict(zip(start_nodes, end_nodes))

    def get_graph_order(self):
        ts = TopologicalSorter(self.graph).static_order()
        ts_list = list(ts)
        ts_list.reverse()
        return ts_list




# graph = {'A': 'B',
#          'D': 'E',
#          'C': 'D',
#          'B': 'C',
# }
#
# ts = TopologicalSorter(graph).static_order()
# print(list(ts).reverse())
# def find_path(graph, start, end, path=[]):
#     path = path + [start]
#     if start == end:
#         return path
#     if not start in graph:
#         return None
#     for node in graph[start]:
#         if node not in path:
#             newpath = find_path(graph, node, end, path)
#             if newpath: return newpath
#     return None
#
# print(find_path(graph, "A", "D"))