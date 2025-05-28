import graphistry
import graphistry.Plottable
import networkx as nx
import dotenv as env
import pandas as pd
import os

class Graphistry:

    def __init__(self):
        env.load_dotenv()
        graphistry.register(
            api=3,
            protocol="https",
            personal_key_id=os.getenv('GRAPHISTRY_PERSONAL_ID', ''),
            personal_key_secret=os.getenv('GRAPHISTRY_PERSONAL_SECRET', ''),
        )

    
    def upload_graph(self, graph: nx.Graph):
        print(graph.is_directed())
        g = graphistry.bind(
            point_color='rgba',
            point_weight='size',
            point_x='x',
            point_y='y',
        ).from_networkx(G=graph)
        g.settings(url_params={'play': 0}).plot()