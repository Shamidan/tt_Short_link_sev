import random
import string


class SimpleShortIdGenerator:
    """Простой генератор"""

    def __init__(self, length: int = 6):
        self.length = length
        self.alphabet = string.ascii_letters + string.digits

    def generate(self) -> str:
        return ''.join(random.choices(self.alphabet, k=self.length))