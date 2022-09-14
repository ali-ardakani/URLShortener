import unittest
from generator import RandomGenerator
from string import ascii_letters, digits
import random

class TestShortUrlGenerator(unittest.TestCase):
         
    def test_len_generator(self):
        generator = RandomGenerator(ascii_letters + digits, 6, 42)
        short_key = generator.generate()
        self.assertEqual(len(short_key), 6)
        
    def test_generator(self):
        generator = RandomGenerator(ascii_letters + digits, 6, 42)
        short_key = generator.generate()
        self.assertEqual(short_key, 'NbrnTP')
        
    def test_unique_generator(self):
        generator = RandomGenerator(ascii_letters + digits, 6, 42)
        short_key = generator.generate()
        short_key2 = generator.generate()
        self.assertNotEqual(short_key, short_key2)
        
    def test_non_repeatable_generator(self):
        keys = set()
        seeds = random.sample(range(1000000), 1000)
        for i in seeds:
            generator = RandomGenerator(ascii_letters + digits, 6, i)
            short_key = generator.generate()
            if short_key in keys:
                self.fail('Repeated key')
            keys.add(short_key)
        
        
if __name__ == '__main__':
    unittest.main()