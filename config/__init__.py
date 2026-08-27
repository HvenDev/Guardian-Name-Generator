import random
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScanConfig:
    username_length: int = 3
    amount: int = 1000
    mode: str = "random"
    seed: Optional[int] = None

    RESULT_DISTRIBUTION = {
        "taken": 0.82,
        "available": 0.035,
        "invalid": 0.06,
        "unknown": 0.085,
    }

    def generate_result(self, rng: random.Random) -> str:
        roll = rng.random()
        cumulative = 0.0
        for status, probability in self.RESULT_DISTRIBUTION.items():
            cumulative += probability
            if roll < cumulative:
                return status
        return "taken"

    @property
    def display_mode(self) -> str:
        return self.mode.upper()

    def validate(self) -> list[str]:
        errors = []
        if self.username_length < 2 or self.username_length > 20:
            errors.append("Username length must be between 2 and 20")
        if self.amount < 1 or self.amount > 100000:
            errors.append("Amount must be between 1 and 100,000")
        if self.mode not in ("random", "sequential", "smart"):
            errors.append("Mode must be random, sequential, or smart")
        return errors
