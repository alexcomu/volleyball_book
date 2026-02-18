from typing import Protocol

from app.domain.models.exercise import Exercise


class ExerciseRepository(Protocol):
    def exists_by_name(self, name: str, exclude_id: str | None = None) -> bool: ...

    def create(self, exercise: Exercise) -> Exercise: ...

    def list(self, include_inactive: bool = False) -> list[Exercise]: ...

    def get_by_id(
        self,
        exercise_id: str,
        include_inactive: bool = False,
    ) -> Exercise | None: ...

    def update(self, exercise: Exercise) -> Exercise: ...
