import pickle
import os

FOLDER = 'cache'

def get_path(cache_key):
    return f"{FOLDER}/{cache_key}.pkl"

def has_cache(cache_key):
    return os.path.isfile(get_path(cache_key))

def save_dict(dictionary, cache_key):
    with open(get_path(cache_key), 'wb') as file:
        pickle.dump(dictionary, file)
    

def retrieve_dict(cache_key):
    if (has_cache(cache_key)):
        with open(get_path(cache_key), 'rb') as file:
            return pickle.load(file)
    else:
        return None