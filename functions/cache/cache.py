from django.core.cache import cache

def setKey(key, value):
    return cache.set(key, value)

def getKey(key):
    return cache.get(key)

def deleteKey(key):
    return cache.delete(key)

def setAllKeys(key, value):
    return cache.set_many(key, value)

def getAllKeyValue():
    # Returns a dictionary of all key-value pairs in the cache
    return cache.get_many()