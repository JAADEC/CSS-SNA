import hashlib
import json
from open_alex import OpenAlex
from cache_data import Cache
from graph import Graph

TERMS = [
    "collective action problem",
    "olson",
    "tullock",
    "public choice",
    "rational choice"
]

CONFLICT_TYPES = [
    "revolution",
    "rebellion",
    "civil war",
    "unrest",
    "uprising"
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

    return open_alex_api.get_references()

if __name__ == '__main__':
    cache_key = get_hash_key()

    api_cache = Cache('api')
    references: dict = api_cache.execute(cache_key, get_api_data)

    print(f"{len(references)} articles retrieved")

    graph = Graph(references, CONFLICT_TYPES)

    graph.import_from_file('all-20')
    graph.statistics()
    graph.ei_index()

    # graph.build_co_citation(
    #     cited_by_cutoff=20
    # )
    # graph.statistics()
    # graph.store_to_file("co-citation-20")