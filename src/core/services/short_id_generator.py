

class ShortIdGenerator:
    pass


import random
import string


class SimpleShortIdGenerator:
    """Простой генератор для первого этапа (не для продакшена)"""

    def __init__(self, length: int = 6):
        self.length = length
        self.alphabet = string.ascii_letters + string.digits

    def generate(self) -> str:
        return ''.join(random.choices(self.alphabet, k=self.length))