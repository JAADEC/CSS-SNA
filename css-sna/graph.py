import networkx as nx
import pandas as pd
import itertools as it
import datetime as dt

class Graph:
    FOLDER = 'data'
    FILE_TIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
    UPDATE_COUNT = 1000000

    def __init__(self, references: dict, directed = False):
        self.references = references
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
                author = ""
            else:
                author = reference['authorships'][0]['author']['display_name']
            self.graph.add_node(
                key,
                label=f"{reference['title']}-{author}",
                relevance_score=reference['relevance_score'],
                publication_date=reference['publication_date'],
                first_author=author
            )
        else:
            print(f"Reference with key {key} not found in references set")

    def statistics(self):
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        density = nx.density(self.graph)
        avg_clustering = nx.average_clustering(self.graph)

        # Print the results
        print()
        print("------------------------------------ STATS ------------------------------------")
        print("Number of nodes:                  ", num_nodes)
        print("Number of edges:                  ", num_edges)
        print("Density:                          ", density)
        print("Average clustering coefficient:   ", avg_clustering)
        print("-------------------------------------------------------------------------------")

    def store_to_file(self, filename: str = None):
        now = dt.datetime.now()
        filedate = now.strftime(self.FILE_TIME_FORMAT)

        if not filename:
            file = f"{self.FOLDER}/{filedate}.gexf"
        else:
            file = f"{self.FOLDER}/{filedate}_{filename}.gexf"
        nx.write_gexf(self.graph, file)

    def build_co_citation(self, cited_by_cutoff = 1, co_cite_cutoff = 1, jaccard_cuttoff = 0.0):
        print("Initiating count dataframe")
        keys = self.references.keys()
        co_matrix = pd.DataFrame(0, index=keys, columns=keys)
        referenced_set = set()

        print("Counting co-citations")
        for refs in self.references.values():
            for referenced in refs['referenced_works']:
                if referenced in self.references:
                    co_matrix.at[referenced, referenced] += 1
                    referenced_set.add(referenced)

            for (a, b) in it.combinations(refs['referenced_works'], 2):
                if a in self.references and b in self.references:
                    co_matrix.at[a, b] += 1
                    co_matrix.at[b, a] += 1

        print(f"Found {len(referenced_set)} cited references in our dataset")

        print("Creating nodes in the graph")
        filtered_set = set()
        for reference_key in referenced_set:
            cited_by = co_matrix.loc[reference_key, reference_key]
            if cited_by >= cited_by_cutoff:
                self.add_reference_node(reference_key)
                filtered_set.add(reference_key)

        print(f"Found {len(filtered_set)} cited references cited by {cited_by_cutoff} or more references")

        print("Add edges to graph")
        count = 0
        for (a, b) in it.combinations(filtered_set, 2):
            count += 1
            if count % self.UPDATE_COUNT == 0:
                print(f"Processed {count // self.UPDATE_COUNT}M edges")

            combination_count = co_matrix.loc[a, b]
            
            if combination_count >= co_cite_cutoff:
                a_count = co_matrix.loc[a, a]
                b_count = co_matrix.loc[b, b]

                jaccard_index = combination_count / (a_count + b_count - combination_count)
                if jaccard_index >= jaccard_cuttoff:
                    self.graph.add_edge(a, b, weight=jaccard_index)


    def build_citation(self):
        print("Creating nodes")
        for reference_key in self.references:
            self.add_reference_node(reference_key)
        
        print("Creating edges")
        for reference_from_key, reference_from in self.references.items():
            for reference_to_key in reference_from['referenced_works']:
                if reference_to_key in self.references:
                    self.graph.add_edge(reference_from_key, reference_to_key)