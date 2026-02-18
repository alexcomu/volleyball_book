from dataclasses import dataclass
from typing import Protocol


class FeatureFlags(Protocol):
    def is_enabled(self, key: str) -> bool: ...


@dataclass(frozen=True)
class InMemoryFeatureFlags(FeatureFlags):
    values: dict[str, bool]

    def is_enabled(self, key: str) -> bool:
        return self.values.get(key, False)
