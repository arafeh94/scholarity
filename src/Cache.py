import os
import pickle
from abc import ABC


class Cache:
    def __init__(self, file):
        self.file = file
        self.content = {}
        if not os.path.exists(file):
            self._save()

    def put(self, name, value):
        self._load()
        self.content[name] = value
        self._save()

    def get(self, name, default=None):
        self._load()
        return self.content[name] if name in self.content else default

    def keys(self):
        self._load()
        return self.content.keys()

    def get_or_set(self, name, if_not_exists):
        self._load()
        if name in self.content:
            return self.content[name]
        self.content[name] = if_not_exists
        self._save()
        return self.content[name]

    def _load(self):
        with open(self.file, 'rb') as f:
            self.content = pickle.load(f)

    def _save(self):
        with open(self.file, 'wb') as f:
            pickle.dump(self.content, f)


class Cacheable(ABC):
    def __init__(self, cache: Cache):
        self.cache = cache

    def save(self):
        to_save = {}
        for k, v in self.__dict__.items():
            if v is not self.cache:
                to_save[k] = v
        self.cache.put(self.__hash__(), to_save)

    def load(self):
        cached = self.cache.get(self.__hash__())
        if not cached:
            return
        for k, v in cached.items():
            self.__dict__[k] = v
