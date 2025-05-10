import hashlib
from open_alex import OpenAlex
from cache_data import Cache
from graph import Graph

FIRST_TERMS = [
    "collective action problem",
    "olson",
    "tullock",
    "public choice",
    "rational choice"
]

SECOND_TERMS = [
    "revolution",
    "rebellion",
    "civil war",
    "unrest",
    "uprising"
]

FILTERS = {
    'type': 'article',
    # 'from_publication_date': '1985-01-01',
    # 'to_publication_date': '2004-12-31'
}

def get_hash_key():
    hash_values = [
        FIRST_TERMS,
        SECOND_TERMS,
        FILTERS
    ]

    return hashlib.sha256(str(hash_values).encode()).hexdigest()

def get_api_data():
    open_alex_api = OpenAlex()
    open_alex_api.reset_references()

    for first_term in FIRST_TERMS:
        for second_term in SECOND_TERMS:
            open_alex_api.get_request([first_term, second_term], FILTERS)

    return open_alex_api.get_references()

if __name__ == '__main__':
    cache_key = get_hash_key()

    api_cache = Cache('api')
    references = api_cache.execute(get_api_data, cache_key)

    print(f"{len(references)} articles retrieved")

    graph = Graph(references)

    graph.build_co_citation(
        cited_by_cutoff=10
    )
    graph.statistics()
    graph.store_to_file("co-citation")