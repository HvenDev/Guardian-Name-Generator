import random
import string
from typing import Generator as Gen


class UsernameGenerator:
    LOWERCASE = string.ascii_lowercase
    DIGITS = string.digits
    ALL_CHARS = LOWERCASE + DIGITS

    def __init__(self, seed: int | None = None):
        self.rng = random.Random(seed)

    def _random_char(self) -> str:
        return self.rng.choice(self.LOWERCASE)

    def _random_digit(self) -> str:
        return self.rng.choice(self.DIGITS)

    def generate_random(self, length: int, count: int) -> list[str]:
        names = []
        for _ in range(count):
            name = ""
            for i in range(length):
                if i == 0:
                    name += self._random_char()
                elif self.rng.random() < 0.3:
                    name += self._random_digit()
                else:
                    name += self._random_char()
            names.append(name)
        return names

    def generate_sequential(self, length: int, count: int) -> list[str]:
        base = self.LOWERCASE[:length] if length <= 26 else self.LOWERCASE
        names = []
        pool = list(self.LOWERCASE)
        for i in range(count):
            name = ""
            idx = i
            for pos in range(length):
                char_idx = idx % len(pool)
                name = pool[char_idx] + name
                idx //= len(pool)
            names.append(name[:length])
        return names

    def generate_smart(self, length: int, count: int) -> list[str]:
        common_prefixes = ["x", "z", "q", "j", "v", "k"]
        common_suffixes = ["x", "z", "q", "j", "v", "k", "0", "1", "2"]
        names = []
        for _ in range(count):
            prefix = self.rng.choice(common_prefixes)
            suffix = self.rng.choice(common_suffixes) if length > 2 else ""
            middle_len = max(0, length - len(prefix) - len(suffix))
            middle = "".join(
                self.rng.choice(self.LOWERCASE) for _ in range(middle_len)
            )
            name = prefix + middle + suffix
            names.append(name[:length])
        return names

    def generate(self, length: int, count: int, mode: str) -> list[str]:
        if mode == "sequential":
            return self.generate_sequential(length, count)
        elif mode == "smart":
            return self.generate_smart(length, count)
        else:
            return self.generate_random(length, count)
