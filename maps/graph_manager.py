import os
import pickle
import hashlib
import osmnx as ox


class GraphManager:
    """
    Global road-network manager.

    Downloads road networks from OpenStreetMap when needed,
    keeps recently used graphs in memory, and stores them on
    disk so they can survive backend restarts.
    """

    def __init__(self, cache_dir="graph_cache"):
        self.graphs = {}
        self.cache_dir = cache_dir

        os.makedirs(self.cache_dir, exist_ok=True)

    def _region_key(self, latitude, longitude):
        """
        Creates a geographic cache key.

        The grid is approximately 10 km x 10 km.
        """
        lat_key = round(latitude, 1)
        lon_key = round(longitude, 1)

        return lat_key, lon_key

    def _cache_path(self, region):
        lat, lon = region

        filename = hashlib.md5(
            f"{lat}_{lon}".encode()
        ).hexdigest()

        return os.path.join(
            self.cache_dir,
            f"{filename}.pkl",
        )

    def _download_graph(self, latitude, longitude):
        print(
            f"Downloading road network near "
            f"{latitude}, {longitude}..."
        )

        graph = ox.graph_from_point(
            (
                latitude,
                longitude,
            ),
            dist=5000,
            network_type="drive",
            simplify=True,
        )

        print(
            f"Road network downloaded for "
            f"{latitude}, {longitude}."
        )

        return graph

    def get_graph(self, latitude, longitude):

        region = self._region_key(
            latitude,
            longitude,
        )

        # 1. Memory cache
        if region in self.graphs:
            print(
                f"Using memory-cached graph "
                f"for {region}."
            )

            return self.graphs[region]

        cache_path = self._cache_path(region)

        # 2. Disk cache
        if os.path.exists(cache_path):

            print(
                f"Loading cached road network "
                f"for {region}..."
            )

            try:

                with open(
                    cache_path,
                    "rb",
                ) as file:

                    graph = pickle.load(file)

                self.graphs[region] = graph

                print(
                    f"Loaded cached road network "
                    f"for {region}."
                )

                return graph

            except Exception as error:

                print(
                    f"Cache could not be loaded: "
                    f"{error}"
                )

        # 3. Download from OpenStreetMap
        graph = self._download_graph(
            latitude,
            longitude,
        )

        # 4. Save to memory
        self.graphs[region] = graph

        # 5. Save to disk
        try:

            with open(
                cache_path,
                "wb",
            ) as file:

                pickle.dump(
                    graph,
                    file,
                    protocol=pickle.HIGHEST_PROTOCOL,
                )

            print(
                f"Saved road network cache "
                f"for {region}."
            )

        except Exception as error:

            print(
                f"Could not save graph cache: "
                f"{error}"
            )

        return graph