import requests
import cache

API_BASE = "https://api.openalex.org/works?"

dictionary = dict()

def reset_articles(): 
    dictionary.clear

def get_articles():
    return dictionary

def normalize(term):
    return '"' + term.lower() + '"'

def get(terms, filters):
    search_terms = " ".join(map(normalize, terms))
    filters = ",".join(f"{key}:{value}" for key, value in filters.items())

    print("")
    print("=== Retrieving works from Open Alex ===")
    print(f"Terms     -> {search_terms}")
    print(f"Filters   -> {filters}")
    print("=======================================")

    return get_all(search_terms, filters)

def get_all(search_terms, filters, cursor='*'):
    payload = {
        'search': search_terms,
        'per-page': 200,
        'filter': filters,
        'cursor': cursor
    }

    response = requests.get(API_BASE, params=payload)

    json_response = response.json()

    count = 0
    dict_start = len(dictionary)
    for result in json_response['results']:
        dictionary[result['id']] = result
        count += 1

    if (json_response['meta']['next_cursor']):
        print(f"Added an additional {len(dictionary) - dict_start} from {count} sources to the dictionary, totalling {len(dictionary)} entries")
        get_all(search_terms, filters, cursor=json_response['meta']['next_cursor'])
    else:
        print(f"Retrieved {json_response['meta']['count']} works with search term: {search_terms}")