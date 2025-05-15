import networkx as nx
import pandas as pd
import itertools as it
import datetime as dt
import os

class Graph:
    FOLDER = 'data'
    FILE_TIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
    UPDATE_COUNT = 1000000
    IMPORT_FORMATS = {
        "graphml": nx.read_graphml,
        "gml": nx.read_gml,
        "gexf": nx.read_gexf,
    }

    def __init__(self, references: dict, conflict_types: list, directed = False):
        self.references = references
        self.conflict_types = conflict_types
        self.directed = directed
        self.reset_graph()

    def reset_graph(self):
        if self.directed:
            self.graph = nx.DiGraph()
        else:
            self.graph = nx.Graph()

    def add_reference_node(self, key):
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
                **conflict_search
            )
        else:
            print(f"Reference with key {key} not found in references set")

    def ei_index(self, module_index: str = "Modularity Class"):
        print("Calculating e-i index")
        external = 0
        internal = 0
        for node1, node2 in self.graph.edges():
            if self.graph.nodes[node1][module_index] == self.graph.nodes[node2][module_index]:
                internal += 1
            else:
                external += 1
        
        ei = (external - internal) / (external + internal)

        self.print_stats({
            "E-I index": ei
        })



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

    def print_stats(self, stats: dict):
        # Print the results
        print()
        print("------------------------------------ STATS ------------------------------------")
        for name, value in stats.items():
            whitespace = ' ' * (40 - len(name))
            print(f"{name}:{whitespace}{value}")
        print("-------------------------------------------------------------------------------")

    def import_from_file(self, filename: str):
        for format, importer in self.IMPORT_FORMATS.items():
            if file := self.get_path(filename, format):
                print(f"Importing '{file}'")
                self.graph = importer(file)
                return
            
        print(f"'{filename}' not found")

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
            file = f"{self.FOLDER}/{filedate}.gexf"
        else:
            file = f"{self.FOLDER}/{filedate}_{filename}.gexf"
        nx.write_gexf(self.graph, file)

    def build_co_citation(self, cited_by_cutoff = 1, cited_by_cutoff_year = None, co_cite_cutoff = 1, jaccard_cuttoff = 0.0, references_cuttoff_year = None):
        print("Calculating referenced by measure")
        referenced_by_count = dict()
        for reference in self.references.values():
            if not cited_by_cutoff_year or reference['publication_year'] >= cited_by_cutoff_year:
                for referenced in reference['referenced_works']:
                    if referenced in self.references and (not references_cuttoff_year or self.references[referenced]['publication_year'] >= references_cuttoff_year):
                        if not referenced in referenced_by_count:
                            referenced_by_count[referenced] = 0
                        referenced_by_count[referenced] += 1

        print(f"Found {len(referenced_by_count)} cited references in our dataset")

        print("Creating nodes in the graph")
        filtered_set = set()
        for reference_key, reference_count in referenced_by_count.items():
            if reference_count >= cited_by_cutoff:
                self.add_reference_node(reference_key)
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
                    self.graph.add_edge(a, b, label=f"{from_reference['title']} - {to_reference['title']}", weight=jaccard_index, jaccard_index=jaccard_index, count=combination_count)


    def build_citation(self):
        print("Creating nodes")
        for reference_key in self.references:
            self.add_reference_node(reference_key)
        
        print("Creating edges")
        for reference_from_key, reference_from in self.references.items():
            for reference_to_key in reference_from['referenced_works']:
                if reference_to_key in self.references:
                    self.graph.add_edge(reference_from_key, reference_to_key)