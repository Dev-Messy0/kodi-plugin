from pathlib import Path

# Cache simple en mémoire pour le script autonome
class SimpleCache:
    def __init__(self):
        self._cache = {}
    
    def get(self, key):
        return self._cache.get(key)
    
    def set(self, key, value):
        self._cache[key] = value
    
    def delete(self, key):
        if key in self._cache:
            del self._cache[key]

# Remplacer StorageServer par SimpleCache
cache = SimpleCache()
ADDON_PATH = Path(__file__).parent.parent  # Remonte à la racine du projet