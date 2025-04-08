import networkx as nx
import matplotlib.pyplot as plt 

def graph():
    # A very simple graph

    # Create a graph 
    G = nx.Graph()

    # Add nodes
    G.add_nodes_from([1, 2, 3])

    # Add edges
    G.add_edges_from([(1, 2), (2, 3), (3, 1)])

    # Plot the graph
    nx.draw(G, with_labels=True)

    print(G.degree)