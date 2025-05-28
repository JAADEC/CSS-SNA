import hashlib
import json
import datetime as dt
from open_alex import OpenAlex
from cache_data import Cache
from graph import Graph

TERMS = [
    "collective action problem",
    "olson",
    "tullock",
    "public choice",
    "rational choice",
    "free riding",
    "free rider",
]

CONFLICT_TYPES = [
    "revolution",
    "rebellion",
    "civil war",
    "unrest",
    "uprising",
    "insurgency",
]

FILTERS = {
    'type': 'article|book-chapter|book|review',
    # 'from_publication_date': '1985-01-01',
    # 'to_publication_date': '2004-12-31'
}

def get_hash_key():
    hash_data = {
        "terms": TERMS,
        "conflict_types": CONFLICT_TYPES,
        "filter": FILTERS
    }

    hashed_value = hashlib.sha256(str(hash_data).encode()).hexdigest()

    hash_data['executed_at'] = dt.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    # Serializing json
    json_data = json.dumps(hash_data, indent=4)
    with open(f"cache/key_overview/{hashed_value}.json", "w") as outfile:
        outfile.write(json_data)

    return hashed_value


def get_api_data():
    open_alex_api = OpenAlex()
    open_alex_api.reset_references()

    for term in TERMS:
        for conflict_type in CONFLICT_TYPES:
            open_alex_api.get_request(term, conflict_type, FILTERS)

    open_alex_api.get_request("collective action", "logic", {"ids.openalex": "https://openalex.org/W4391965190"})

    return open_alex_api.get_references()

if __name__ == '__main__':
    cache_key = get_hash_key()

    api_cache = Cache('api')
    references: dict = api_cache.execute(cache_key, get_api_data)

    print(f"{len(references)} articles retrieved")

    graph = Graph(references, CONFLICT_TYPES)

    graph.build_co_citation(
        cited_by_cutoff=10,
        relevance_score_cuttoff=5.0
    )
    graph.statistics()
    graph.use_reference_graph("structure")
    graph.statistics()
    graph.upload_to_graphistry()
    # graph.ei_index()
    # graph.betweenness(0, 3)
    # graph.get_hex_color()
    # graph.count(most_common=10)

    # graph.store_to_file("all")