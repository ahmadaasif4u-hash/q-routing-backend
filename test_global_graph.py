from maps.graph_manager import GraphManager

manager = GraphManager()

print("\n# GLOBAL GRAPH TEST")
print("===================")

print("\nLoading Dubai...")
dubai = manager.get_graph(25.2048, 55.2708)
print("Dubai nodes:", len(dubai.nodes))

print("\nLoading London...")
london = manager.get_graph(51.5074, -0.1278)
print("London nodes:", len(london.nodes))

print("\nGLOBAL GRAPH TEST PASSED")