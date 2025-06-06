import networkx as nx
import pandas as pd
import itertools as it
import datetime as dt
import collections as cl
import numbers as num
import os
from graphistry_api import Graphistry

class Graph:
    FOLDER = 'data'
    FILE_TIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
    SPLIT_CHARACTER = ';'
    UPDATE_COUNT = 1000000
    IMPORT_FORMATS = {
        "graphml": nx.read_graphml,
        "gml": nx.read_gml,
        "gexf": nx.read_gexf,
    }

    CONVERTED_ATTRIBUTES = {
        "Modularity Class": 'modul_class', 
        "Eigenvector Centrality": 'eig_centr',
        "size": "size",
        "r": "r",
        "g": "g",
        "b": "b",
        "x": "x",
        "y": "y",
    }

    KEY_MAPPING = {
        "https://openalex.org/W2120946983": "https://openalex.org/W4391965190",
        "https://openalex.org/W2324656367": "https://openalex.org/W4391965190",
        "https://openalex.org/W2328035621": "https://openalex.org/W4391965190",
    }

    def __init__(self, references: dict, conflict_types: list):
        self.references = references
        self.conflict_types = conflict_types
        self.reset_graph()

    def reset_graph(self):
        self.graph = nx.Graph()

    def add_reference_node(self, key, cited_by: int = -1):
        if key in self.references:
            reference = self.references.get(key)

            if len(reference['authorships']) == 0:
                author = "Unknown"
            else:
                author = reference['authorships'][0]['author']['display_name']

            search_data: dict = reference['search_data']
            conflict_search = {c: search_data.get(c) or 0 for c in self.conflict_types}

            self.graph.add_node(
                key,
                label=f"{reference['title']} - {author}",
                relevance_score=reference['relevance_score'],
                publication_date=reference['publication_date'],
                first_author=author,
                cited_by=reference['cited_by_count'],
                cited_by_dataset=cited_by,
                type=reference['type'],
                topics=self.SPLIT_CHARACTER.join([topic['display_name'] for topic in reference['topics']]),
                keywords=self.SPLIT_CHARACTER.join([keyword['display_name'] for keyword in reference['keywords']]),
                concepts=self.SPLIT_CHARACTER.join([concept['display_name'] for concept in reference['concepts']]),
                **conflict_search
            )
        else:
            print(f"Reference with key {key} not found in references set")

    def key_by_modularity(self, module_index: str = "modul_class"):
        modularities = dict()
        
        for node_id in self.graph.nodes():
            if not module_index in self.graph.nodes[node_id]:
                continue

            module_class = self.graph.nodes[node_id][module_index]
            if not module_class in modularities:
                modularities[module_class] = []

            modularities[module_class].append(node_id)

        return modularities

    def ei_index(self, module_index: str = "modul_class"):
        print("Calculating e-i index")
        external = 0
        internal = 0
        for node1, node2 in self.graph.edges():
            if (not module_index in self.graph.nodes[node1]) or (not module_index in self.graph.nodes[node2]):
                continue

            if self.graph.nodes[node1][module_index] == self.graph.nodes[node2][module_index]:
                internal += 1
            else:
                external += 1
        
        ei = (external - internal) / (external + internal)

        self.print_stats({
            "E-I index": ei
        })

    def betweenness(self, cluster_source, cluster_traget, weights: str = None, module_index: str = "modul_class"):
        if cluster_source == cluster_traget:
            print("Clusters cannot be the same")
            return

        modularities = self.key_by_modularity(module_index)

        if not cluster_source in modularities:
            print(f"Cannot find cluster {cluster_source}, possible clusters: {list(modularities.keys())}")
            return
        
        if not cluster_traget in modularities:
            print(f"Cannot find cluster {cluster_traget}, possible clusters: {list(modularities.keys())}")
            return

        betweenness = nx.betweenness_centrality_subset(
            self.graph,
            sources=modularities.get(cluster_source),
            targets=modularities.get(cluster_traget),
            normalized=True,
            weight=weights,
        )

        sorted_bridges = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)

        self.print_stats({
            "Nodes": f"{cluster_source} <> {cluster_traget}",
            0: "Most common bridges",
            **dict([(self.graph.nodes[key]['label'], value) for (key, value) in sorted_bridges[:10]]),
        }, 120)

    def count(self, most_common: int = 3, module_index: str = "modul_class"):
        flat_map = lambda f, xs: (y for ys in xs for y in f(ys))

        modularities = self.key_by_modularity(module_index)

        for modularity_class, modularity_nodes in modularities.items():
            total = len(modularity_nodes)

            topics = cl.Counter(flat_map(lambda node_id: self.graph.nodes[node_id]['topics'].split(self.SPLIT_CHARACTER), modularity_nodes))
            keywords = cl.Counter(filter(None, flat_map(lambda node_id: self.graph.nodes[node_id]['keywords'].split(self.SPLIT_CHARACTER), modularity_nodes)))
            concepts = cl.Counter(flat_map(lambda node_id: self.graph.nodes[node_id]['concepts'].split(self.SPLIT_CHARACTER), modularity_nodes))

            self.print_stats({
                "Modularity class": modularity_class,
                "Total included in class": total,
                0: "Topics",
                **dict([(key, f"{count/total:.2%} | {count}") for (key, count) in topics.most_common(most_common)]),
                1: "Concepts",
                **dict([(key, f"{count/total:.2%} | {count}") for (key, count) in concepts.most_common(most_common)]),
                2: "Keywords",
                **dict([(key, f"{count/total:.2%} | {count}") for (key, count) in keywords.most_common(most_common)]),
            }, 60)


    def statistics(self):
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        density = nx.density(self.graph)
        avg_clustering = nx.average_clustering(self.graph)

        self.print_stats({
            "Number of nodes": num_nodes,
            "Number of edges": num_edges,
            "Density": density,
            "Average clustering coefficient": avg_clustering,
        })

    def get_hex_color(self, module_index: str = "modul_class"):
        modularities = self.key_by_modularity(module_index)

        for (cluster_key, references) in modularities.items():
            print(cluster_key)
            reference = self.graph.nodes[references[0]]
            print('#%02x%02x%02x' % (reference['r'], reference['g'], reference['b']))

    def print_stats(self, stats: dict, spaces: int = 40):
        # Print the results
        print()
        print("------------------------------------ STATS ------------------------------------")
        for name, value in stats.items():
            if isinstance(name, num.Number):
                print()
                print(f"------------------------------------ {value.upper()}")
                continue

            whitespace = ' ' * (spaces - len(name))
            print(f"{name}:{whitespace}{value}")
        print("-------------------------------------------------------------------------------")

    def use_reference_graph(self, filename: str, remove_nodes: bool = True):
        reference: Graph = None

        for format, importer in self.IMPORT_FORMATS.items():
            if file := self.get_path(filename, format):
                print(f"Importing '{file}'")
                reference = importer(file)
                break
        
        if not reference:
            print(f"'{filename}' not found")
            return
        else:
            print(f"Reference graph contains {len(reference.nodes())} nodes")

        removed = set()
        attributes = dict()

        for node_id in self.graph.nodes():
            if not node_id in reference.nodes():
                removed.add(node_id)
            else:
                attributes[node_id] = {}
                for attr_from, attr_to in self.CONVERTED_ATTRIBUTES.items():
                    attributes[node_id][attr_to] = reference.nodes[node_id][attr_from]

                rgba = 255 | (reference.nodes[node_id]['b'] << 8) | (reference.nodes[node_id]['g'] << 16) | (reference.nodes[node_id]['r'] << 24)  
                attributes[node_id]['rgba'] = rgba


        if remove_nodes:
            print(f"Will remove {len(removed)} nodes from graph")
            self.graph.remove_nodes_from(removed)

        print(f"Convert attributes from reference graph")
        nx.set_node_attributes(self.graph, attributes)

    def get_path(self, filename: str, extention: str):
        file = file = f"{self.FOLDER}/{filename}.{extention}"
        if os.path.isfile(file):
            return file
        else:
            return None

    def store_to_file(self, filename: str = None):
        now = dt.datetime.now()
        filedate = now.strftime(self.FILE_TIME_FORMAT)

        if not filename:
            file = f"{self.FOLDER}/{filedate}"
        else:
            file = f"{self.FOLDER}/{filedate}_{filename}"
        nx.write_gexf(self.graph, f"{file}.gexf")
        nx.write_graphml(self.graph, f"{file}.graphml", named_key_ids=True)

    def upload_to_graphistry(self):
        graphistry = Graphistry()        
        graphistry.upload_graph(self.graph)
        

        # graphistry.register(api=3, protocol="https", )

    def build_co_citation(self, cited_by_cutoff = 1, cited_by_cutoff_year = None, co_cite_cutoff = 1, jaccard_cuttoff = 0.0, references_cuttoff_year = None, relevance_score_cuttoff = 0.0):
        print("Calculating referenced by measure")
        referenced_by_count = dict()
        for reference in self.references.values():
            if not cited_by_cutoff_year or reference['publication_year'] >= cited_by_cutoff_year:
                for referenced in reference['referenced_works']:
                    referenced = self.KEY_MAPPING.get(referenced, referenced)

                    if referenced in self.references and (not references_cuttoff_year or self.references[referenced]['publication_year'] >= references_cuttoff_year) and self.references[referenced]['relevance_score'] > relevance_score_cuttoff:
                        if not referenced in referenced_by_count:
                            referenced_by_count[referenced] = 0
                        referenced_by_count[referenced] += 1

        print(f"Found {len(referenced_by_count)} cited references in our dataset")

        print("Creating nodes in the graph")
        filtered_set = set()
        for reference_key, reference_count in referenced_by_count.items():
            if reference_count >= cited_by_cutoff:
                self.add_reference_node(reference_key, reference_count)
                filtered_set.add(reference_key)

        if cited_by_cutoff_year:
            print(f"Found {len(filtered_set)} cited references cited by {cited_by_cutoff} or more references since {cited_by_cutoff_year}")
        else:
            print(f"Found {len(filtered_set)} cited references cited by {cited_by_cutoff} or more references")

        print("Counting co-citations")
        co_matrix = pd.DataFrame(0, index=list(filtered_set), columns=list(filtered_set))
        for reference in self.references.values():
            for (a, b) in it.combinations(reference['referenced_works'], 2):
                if a in filtered_set and b in filtered_set:
                    co_matrix.at[a, b] += 1
                    co_matrix.at[b, a] += 1        

        print("Add edges to graph")
        count = 0
        for (a, b) in it.combinations(filtered_set, 2):
            count += 1
            if count % self.UPDATE_COUNT == 0:
                print(f"Processed {count // self.UPDATE_COUNT}M edges")

            combination_count = co_matrix.loc[a, b]
            
            if combination_count >= co_cite_cutoff:
                a_count = referenced_by_count[a]
                b_count = referenced_by_count[b]

                jaccard_index = combination_count / (a_count + b_count - combination_count)
                from_reference = self.references.get(a)
                to_reference = self.references.get(b)
                if jaccard_index >= jaccard_cuttoff:
                    self.graph.add_edge(a, b, label=f"{from_reference['title']} - {to_reference['title']}", weight=jaccard_index, jaccard_index=jaccard_index, count=combination_count, type="Undirected")

    def build_citation(self):
        print("Creating nodes")
        for reference_key in self.references:
            self.add_reference_node(reference_key)
        
        print("Creating edges")
        for reference_from_key, reference_from in self.references.items():
            for reference_to_key in reference_from['referenced_works']:
                if reference_to_key in self.references:
                    self.graph.add_edge(reference_from_key, reference_to_key)