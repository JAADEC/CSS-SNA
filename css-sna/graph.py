import networkx as nx
import pandas as pd
import itertools as it

FOLDER = 'data'

graph: nx.Graph = nx.Graph()

def create_nodes(articles: dict):
    print("Creating nodes in the graph")
    for article_key, article in articles.items():
        graph.add_node(
            article_key,
            label=article['title'],
            # relevance_score=article['relevance_score'],
            # publication_year=article['publication_date']
        )

def statistics():
    # Number of nodes
    num_nodes = graph.number_of_nodes()

    # Number of edges
    num_edges = graph.number_of_edges()

    # Density
    density = nx.density(graph)

    # Average clustering coefficient
    avg_clustering = nx.average_clustering(graph)

    # Print the results
    print("Number of nodes:", num_nodes)
    print("Number of edges:", num_edges)
    print("Density:", density)
    print("Average clustering coefficient:", avg_clustering)

def store(filename: str):
    nx.write_gexf(graph, f"{FOLDER}/{filename}.gexf")

def build_co_citation(articles: dict):
    print("Initiating count dataframe")
    keys = articles.keys()
    co_matrix = pd.DataFrame(0, index=keys, columns=keys)
    referenced_articles = set()

    print("Counting co-citations")
    for refs in articles.values():
        for referenced_article in refs['referenced_works']:
            if referenced_article in articles:
                co_matrix.at[referenced_article, referenced_article] += 1
                referenced_articles.add(referenced_article)

        for (a, b) in it.combinations(refs['referenced_works'], 2):
            if a in articles and b in articles:
                co_matrix.at[a, b] += 1
                co_matrix.at[b, a] += 1

    print(f"Found {len(referenced_articles)} cited articles in our dataset")

    print("Creating nodes in the graph")
    filtered_articles = set()
    for article_key in referenced_articles:
        cited_by = co_matrix.loc[article_key, article_key]
        if cited_by > 9:
            graph.add_node(
                article_key,
                label=articles.get(article_key)['title'],
                # relevance_score=article['relevance_score'],
                # publication_year=article['publication_date']
            )
            filtered_articles.add(article_key)

    print(f"Found {len(filtered_articles)} cited articles that were cited often in our dataset")

    print("Add edges to graph")
    count = 0
    for (a, b) in it.combinations(filtered_articles, 2):
        count += 1
        if count % 1000000 == 0:
            print(f"Processed {count // 1000000}M edges")

        combination_count = co_matrix.loc[a, b]
        
        if combination_count != 0:
            a_count = co_matrix.loc[a, a]
            b_count = co_matrix.loc[b, b]

            jaccard_index = combination_count / (a_count + b_count - combination_count)
            graph.add_edge(a, b, weight=jaccard_index)


def build_citation(articles: dict):
    create_nodes(articles)
        
    for article_from_key, article_from in articles.items():
        for article_to_key in article_from['referenced_works']:
            if article_to_key in articles:
                graph.add_edge(article_from_key, article_to_key)