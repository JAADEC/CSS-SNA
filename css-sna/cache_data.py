import pickle
import os

class Cache:
    FOLDER = 'cache'

    def __init__(self, folder: str):
        self.folder = f"cache/{folder}"

    def execute(self, function, cache_key: str):
        print(f"Executing function with cache key: '{cache_key}'")

        if cache_key and self.has_cache(cache_key):
            print("Cache hit")
            return self.retrieve_cache(cache_key)
        else:
            print("Cache miss, executing function")
            data = function()
            self.save_cache(data, cache_key)
            return data

    def get_path(self, cache_key):
        return f"{self.folder}/{cache_key}.pkl"

    def has_cache(self, cache_key):
        return os.path.isfile(self.get_path(cache_key))

    def save_cache(self, data, cache_key):
        with open(self.get_path(cache_key), 'wb') as file:
            pickle.dump(data, file)
        

    def retrieve_cache(self, cache_key):
        if (self.has_cache(cache_key)):
            with open(self.get_path(cache_key), 'rb') as file:
                return pickle.load(file)
        else:
            return None