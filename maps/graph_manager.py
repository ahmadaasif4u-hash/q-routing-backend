import gc
import os
import time

import osmnx as ox


class GraphManager:

    def __init__(self):
        self.graph = None
        self.current_region = None

        # Multiple Overpass servers.
        self.overpass_servers = [
            "https://overpass-api.de/api",
            "https://overpass.kumi.systems/api",
            "https://overpass.private.coffee/api",
        ]

        self.cache_dir = "road_cache"

        os.makedirs(self.cache_dir, exist_ok=True)

    def _cache_path(self, region):
        lat, lon = region
        return os.path.join(
            self.cache_dir,
            f"road_{lat}_{lon}.graphml",
        )

    def _load_cache(self, region):
        path = self._cache_path(region)

        if not os.path.exists(path):
            return None

        try:
            print(f"Loading cached road network: {path}")

            graph = ox.load_graphml(path)

            print(
                f"Cached road network loaded: "
                f"{len(graph.nodes)} nodes, "
                f"{len(graph.edges)} edges."
            )

            return graph

        except Exception as error:
            print(
                f"WARNING: Could not load road cache: "
                f"{error}"
            )

            try:
                os.remove(path)
            except OSError:
                pass

            return None

    def _save_cache(self, graph, region):
        path = self._cache_path(region)

        try:
            ox.save_graphml(graph, filepath=path)

            print(
                f"Saved road network cache: {path}"
            )

        except Exception as error:
            print(
                f"WARNING: Could not save road cache: "
                f"{error}"
            )

    def _download_graph(self, latitude, longitude):

        last_error = None

        for server in self.overpass_servers:

            try:
                print(
                    f"Trying Overpass server: {server}"
                )

                ox.settings.overpass_url = server

                graph = ox.graph_from_point(
                    (latitude, longitude),
                    dist=3000,
                    network_type="drive",
                    simplify=True,
                    retain_all=False,
                    truncate_by_edge=True,
                )

                print(
                    f"Road network downloaded: "
                    f"{len(graph.nodes)} nodes, "
                    f"{len(graph.edges)} edges."
                )

                return graph

            except Exception as error:

                last_error = error

                print(
                    f"WARNING: Overpass server failed: "
                    f"{server}"
                )

                print(
                    f"Reason: {error}"
                )

                time.sleep(1)

        raise RuntimeError(
            "All Overpass servers failed. "
            f"Last error: {last_error}"
        )

    def get_graph(self, latitude, longitude):

        # Coarse region key.
        # This allows nearby requests to reuse
        # the same road network.
        region = (
            round(latitude, 2),
            round(longitude, 2),
        )

        # Reuse currently loaded graph.
        if (
            self.graph is not None
            and self.current_region == region
        ):
            print(
                "Using currently loaded road network."
            )

            return self.graph

        # Release previous graph.
        if self.graph is not None:

            del self.graph

            self.graph = None

            gc.collect()

        print(
            f"Loading road network for "
            f"{latitude}, {longitude}..."
        )

        # FIRST: try local persistent cache.
        graph = self._load_cache(region)

        # SECOND: download only if cache does not exist.
        if graph is None:

            graph = self._download_graph(
                latitude,
                longitude,
            )

            # Save for future requests.
            self._save_cache(
                graph,
                region,
            )

        self.graph = graph

        self.current_region = region

        gc.collect()

        return self.graph