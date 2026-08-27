import random
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from config import ScanConfig
from generator.username import UsernameGenerator


@dataclass
class ScanResult:
    username: str
    status: str


@dataclass
class ScanStats:
    checked: int = 0
    total: int = 0
    available: int = 0
    taken: int = 0
    invalid: int = 0
    unknown: int = 0
    elapsed: float = 0.0
    speed: float = 0.0
    available_names: list[str] = field(default_factory=list)


class Scanner:
    def __init__(self, config: ScanConfig, on_progress: Optional[Callable] = None):
        self.config = config
        self.on_progress = on_progress
        self.running = False
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def scan(self) -> ScanStats:
        self.running = True
        self._cancelled = False

        seed = self.config.seed if self.config.seed is not None else random.randint(0, 2**31)
        gen = UsernameGenerator(seed)
        rng = random.Random(seed + 1)

        usernames = gen.generate(
            self.config.username_length,
            self.config.amount,
            self.config.mode,
        )

        stats = ScanStats(total=len(usernames))
        start_time = time.perf_counter()

        batch_size = max(1, len(usernames) // 200)

        for i, username in enumerate(usernames):
            if self._cancelled:
                break

            status = self.config.generate_result(rng)
            stats.checked += 1

            if status == "available":
                stats.available += 1
                stats.available_names.append(username)
            elif status == "taken":
                stats.taken += 1
            elif status == "invalid":
                stats.invalid += 1
            else:
                stats.unknown += 1

            stats.elapsed = time.perf_counter() - start_time
            stats.speed = stats.checked / stats.elapsed if stats.elapsed > 0 else 0

            if self.on_progress and (i % batch_size == 0 or i == len(usernames) - 1):
                self.on_progress(stats)

            if i < len(usernames) - 1:
                time.sleep(0.001)

        stats.elapsed = time.perf_counter() - start_time
        stats.speed = stats.checked / stats.elapsed if stats.elapsed > 0 else 0
        self.running = False
        return stats
