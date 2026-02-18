from typing import Protocol

from app.domain.models.exercise import Exercise


class ExerciseRepository(Protocol):
    def exists_by_name(self, name: str) -> bool: ...

    def create(self, exercise: Exercise) -> Exercise: ...
