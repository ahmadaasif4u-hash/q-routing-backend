
import os
import gc
import osmnx as ox


class GraphManager:

    def __init__(self):
        self.graph = None
        self.current_region = None

    def get_graph(self, latitude, longitude):

        # Use a coarse region key so nearby requests can reuse
        # the same road network.
        region = (
            round(latitude, 2),
            round(longitude, 2),
        )

        # Reuse the currently loaded graph when possible.
        if self.graph is not None and self.current_region == region:
            return self.graph

        # Release the previous graph before loading another one.
        if self.graph is not None:
            del self.graph
            self.graph = None
            gc.collect()

        print(
            f"Loading road network for "
            f"{latitude}, {longitude}..."
        )

        # Smaller network to keep Render memory usage low.
        graph = ox.graph_from_point(
            (latitude, longitude),
            dist=3000,
            network_type="drive",
            simplify=True,
            retain_all=False,
            truncate_by_edge=True,
        )

        print(
            f"Road network loaded: "
            f"{len(graph.nodes)} nodes, "
            f"{len(graph.edges)} edges."
        )

        # Keep only the currently required graph.
        self.graph = graph
        self.current_region = region

        gc.collect()

        return self.graph

