import hashlib
import random

class RandomGenerator(object):
    """Generates unique random strings"""
    def __init__(self, characters: str, length: int, seed: int = 0) -> None:
        self.characters = characters
        self.length = length
        self.seed = seed
    
    def generate(self) -> str:
        random.seed(self.seed)
        short_url = ''.join(random.choices(self.characters, k=self.length))
        self.seed += 1
        return short_url
