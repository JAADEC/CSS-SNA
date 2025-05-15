import requests
import hashlib
from cache_data import Cache

class OpenAlex:
    API_BASE = "https://api.openalex.org/works?"
    STORED_KEYS = [
        "authorships",
        "search_data",
        "title",
        "relevance_score",
        "publication_date",
        "publication_year",
        "referenced_works"
    ]

    def __init__(self):
        self.dictionary = dict()
        self.cache = Cache('open_alex', log=False)

    def reset_references(self): 
        self.dictionary.clear

    def get_references(self,):
        return self.dictionary

    def normalize(self, term):
        return '"' + term.lower() + '"'
    
    def compress(self, result):
        return {key: result[key] for key in result if key in self.STORED_KEYS}
    
    def get_hash_key(self, payload: dict):
        return hashlib.sha256(str(payload).encode()).hexdigest()

    def get_request(self, term, conflict_type, filters):
        filters = ",".join(f"{key}:{value}" for key, value in filters.items())

        print()
        print("----------------------- Retrieving works from Open Alex -----------------------")
        print(f"Term           -> {term}")
        print(f"Conflict type  -> {conflict_type}")
        print(f"Filters        -> {filters}")
        print("-------------------------------------------------------------------------------")

        return self.get_all(term, conflict_type, filters)

    def get_all(self, term, conflict_type, filters, cursor='*'):
        search_terms = " ".join(map(self.normalize, [term, conflict_type]))
        payload = {
            'mailto': 'jaap.dechering@student.uva.nl',
            'search': search_terms,
            'per-page': 200,
            'filter': filters,
            'cursor': cursor
        }

        cache_key = self.get_hash_key(payload)
        response = self.cache.execute(cache_key, requests.get, url=self.API_BASE, params=payload)
        json_response = response.json()

        count = 0
        dict_start = len(self.dictionary)
        for result in json_response['results']:
            if not result['id'] in self.dictionary:
                self.dictionary[result['id']] = self.compress(result)
                self.dictionary[result['id']]['search_data'] = {}
            else:
                self.dictionary[result['id']]['relevance_score'] += result['relevance_score']
            self.dictionary[result['id']]['search_data'][conflict_type] = 1
            count += 1

        if (json_response['meta']['next_cursor']):
            print(f"Added an additional {len(self.dictionary) - dict_start} from {count} sources to the dictionary, totalling {len(self.dictionary)} entries")
            self.get_all(term, conflict_type, filters, cursor=json_response['meta']['next_cursor'])
        else:
            print(f"Retrieved {json_response['meta']['count']} works with search term: {search_terms}")