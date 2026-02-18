from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from app.application.use_cases.create_exercise import DuplicateExerciseNameError
from app.application.use_cases.exercise_crud import (
    DeleteExerciseUseCase,
    ExerciseNotFoundError,
    GetExerciseUseCase,
    ListExercisesUseCase,
    UpdateExerciseCommand,
    UpdateExerciseUseCase,
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


def _exercise(
    exercise_id: str,
    name: str,
    *,
    is_active: bool = True,
) -> Exercise:
    now = datetime.now(tz=UTC)
    return Exercise(
        id=exercise_id,
        name=name,
        description="desc",
        tags=["team"],
        categories=["warmup"],
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


def test_list_exercises_use_case_returns_only_active_by_default() -> None:
    repository = InMemoryExerciseRepository(
        saved=[
            _exercise("1", "A", is_active=True),
            _exercise("2", "B", is_active=False),
        ],
    )
    use_case = ListExercisesUseCase(repository=repository)

    result = use_case.execute()

    assert [item.id for item in result] == ["1"]


def test_get_exercise_use_case_raises_when_not_found() -> None:
    repository = InMemoryExerciseRepository(saved=[])
    use_case = GetExerciseUseCase(repository=repository)

    with pytest.raises(ExerciseNotFoundError):
        use_case.execute("missing")


def test_update_exercise_use_case_updates_selected_fields() -> None:
    repository = InMemoryExerciseRepository(saved=[_exercise("1", "Serve Drill")])
    use_case = UpdateExerciseUseCase(
        repository=repository,
        allowed_categories=ALLOWED_CATEGORIES,
    )

    result = use_case.execute(
        UpdateExerciseCommand(
            exercise_id="1",
            name="Defense Drill",
            tags=["Team", "TEAM"],
            categories=["Difesa"],
            name_provided=True,
            tags_provided=True,
            categories_provided=True,
        ),
    )

    assert result.name == "Defense Drill"
    assert result.tags == ["team"]
    assert result.categories == ["difesa"]


def test_update_exercise_use_case_raises_on_duplicate_name() -> None:
    repository = InMemoryExerciseRepository(
        saved=[_exercise("1", "Serve Drill"), _exercise("2", "Defense Drill")],
    )
    use_case = UpdateExerciseUseCase(
        repository=repository,
        allowed_categories=ALLOWED_CATEGORIES,
    )

    with pytest.raises(DuplicateExerciseNameError):
        use_case.execute(
            UpdateExerciseCommand(
                exercise_id="1",
                name="Defense Drill",
                name_provided=True,
            ),
        )


def test_delete_exercise_use_case_soft_deletes() -> None:
    repository = InMemoryExerciseRepository(saved=[_exercise("1", "Serve Drill")])
    use_case = DeleteExerciseUseCase(repository=repository)

    use_case.execute("1")

    stored = repository.get_by_id("1", include_inactive=True)
    assert stored is not None
    assert stored.is_active is False
