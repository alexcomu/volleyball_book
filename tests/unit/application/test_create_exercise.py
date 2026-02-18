from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.application.use_cases.create_exercise import (
    CreateExerciseCommand,
    CreateExerciseUseCase,
    DuplicateExerciseNameError,
)
from app.domain.models.exercise import Exercise
from app.domain.repositories.exercise_repository import ExerciseRepository

ALLOWED_CATEGORIES = {"warmup", "ricezione", "servizio", "rigiocata", "difesa"}


@dataclass
class InMemoryExerciseRepository(ExerciseRepository):
    saved: list[Exercise]

    def exists_by_name(self, name: str, exclude_id: str | None = None) -> bool:
        normalized = name.strip().lower()
        return any(
            item.name.lower() == normalized and item.id != exclude_id
            for item in self.saved
        )

    def create(self, exercise: Exercise) -> Exercise:
        self.saved.append(exercise)
        return exercise

    def list(self, include_inactive: bool = False) -> list[Exercise]:
        if include_inactive:
            return self.saved
        return [item for item in self.saved if item.is_active]

    def get_by_id(
        self, exercise_id: str, include_inactive: bool = False
    ) -> Exercise | None:
        for item in self.saved:
            if item.id == exercise_id and (include_inactive or item.is_active):
                return item
        return None

    def update(self, exercise: Exercise) -> Exercise:
        for index, existing in enumerate(self.saved):
            if existing.id == exercise.id:
                self.saved[index] = exercise
                return exercise
        raise AssertionError("Exercise not found in in-memory repository.")


def test_create_exercise_use_case_persists_valid_exercise() -> None:
    repository = InMemoryExerciseRepository(saved=[])
    use_case = CreateExerciseUseCase(
        repository=repository,
        allowed_categories=ALLOWED_CATEGORIES,
    )

    exercise = use_case.execute(
        CreateExerciseCommand(
            name="Serve Receive Drill",
            description="Three pass rotation",
            tags=["serve", "team"],
            categories=["Ricezione", "ricezione", "Difesa"],
        ),
    )

    assert exercise.name == "Serve Receive Drill"
    assert exercise.description == "Three pass rotation"
    assert exercise.tags == ["serve", "team"]
    assert exercise.categories == ["ricezione", "difesa"]
    assert len(repository.saved) == 1
    assert UUID(exercise.id)
    assert isinstance(exercise.created_at, datetime)
    assert exercise.created_at.tzinfo == UTC


def test_create_exercise_use_case_raises_on_duplicate_name() -> None:
    now = datetime.now(tz=UTC)
    existing = Exercise(
        id="24e4e7eb-e0d8-47f6-a3db-22908995ea4b",
        name="Serve Receive Drill",
        description="desc",
        tags=["serve"],
        categories=["ricezione"],
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    repository = InMemoryExerciseRepository(saved=[existing])
    use_case = CreateExerciseUseCase(
        repository=repository,
        allowed_categories=ALLOWED_CATEGORIES,
    )

    with pytest.raises(DuplicateExerciseNameError):
        use_case.execute(
            CreateExerciseCommand(
                name=" Serve Receive Drill ",
                description="another",
                tags=[],
                categories=["warmup"],
            ),
        )
