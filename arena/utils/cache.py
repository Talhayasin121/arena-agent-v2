import os
import json

class Cache:
    def __init__(self, path=".arena_cache"):
        self.path = path
        if not os.path.exists(path): os.makedirs(path)
    
    def get(self, key):
        fpath = os.path.join(self.path, f"{key}.json")
        if os.path.exists(fpath):
            with open(fpath, "r") as f: return json.load(f)
        return None
    
    def set(self, key, value):
        with open(os.path.join(self.path, f"{key}.json"), "w") as f:
            json.dump(value, f)

cache = Cache()
