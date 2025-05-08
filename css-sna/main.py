import hashlib
import open_alex
import cache
import graph

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
    'type': 'article'
}

def get_hash_key():
    hash_values = [
        FIRST_TERMS,
        SECOND_TERMS,
        FILTERS
    ]

    return hashlib.sha256(str(hash_values).encode()).hexdigest()

def get_api_data(hash_key = None):
    print(f"Referencing API data with key: '{hash_key}'")

    if hash_key and cache.has_cache(hash_key):
        print("Cache hit")
        return cache.retrieve_dict(hash_key)
    else:
        print("Cache miss, falling back to API calls")
        open_alex.reset_articles()

        for first_term in FIRST_TERMS:
            for second_term in SECOND_TERMS:
                open_alex.get([first_term, second_term], FILTERS)

        articles = open_alex.get_articles()
        cache.save_dict(articles, hash_key)
        return articles

if __name__ == '__main__':
    hash_key = get_hash_key()

    articles = get_api_data(hash_key)
    print(f"{len(articles)} articles retrieved")

    graph.build_co_citation(articles)
    graph.statistics()
    graph.store(f"co_{hash_key}")