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


@dataclass
class InMemoryExerciseRepository(ExerciseRepository):
    saved: list[Exercise]

    def exists_by_name(self, name: str) -> bool:
        normalized = name.strip().lower()
        return any(item.name.lower() == normalized for item in self.saved)

    def create(self, exercise: Exercise) -> Exercise:
        self.saved.append(exercise)
        return exercise


def test_create_exercise_use_case_persists_valid_exercise() -> None:
    repository = InMemoryExerciseRepository(saved=[])
    use_case = CreateExerciseUseCase(repository=repository)

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
    use_case = CreateExerciseUseCase(repository=repository)

    with pytest.raises(DuplicateExerciseNameError):
        use_case.execute(
            CreateExerciseCommand(
                name=" Serve Receive Drill ",
                description="another",
                tags=[],
                categories=["warmup"],
            ),
        )
