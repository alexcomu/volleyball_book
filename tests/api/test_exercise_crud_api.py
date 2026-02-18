from dataclasses import dataclass
from datetime import UTC, datetime

import pytest
from fastapi import HTTPException, Request

from app.api.routers.exercises import (
    delete_exercise,
    get_exercise,
    list_exercises,
    update_exercise,
)
from app.api.schemas.exercise import UpdateExerciseRequest
from app.application.use_cases.exercise_crud import (
    DeleteExerciseUseCase,
    GetExerciseUseCase,
    ListExercisesUseCase,
    UpdateExerciseUseCase,
)
from app.domain.models.exercise import Exercise
from app.domain.repositories.exercise_repository import ExerciseRepository
from app.shared.feature_flags import InMemoryFeatureFlags

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


def _build_request(method: str, path: str) -> Request:
    request = Request(
        {
            "type": "http",
            "method": method,
            "path": path,
            "headers": [],
        },
    )
    request.state.request_id = "test-request-id"
    return request


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


def test_list_exercises_returns_active_items_only() -> None:
    repository = InMemoryExerciseRepository(
        saved=[
            _exercise("1", "A", is_active=True),
            _exercise("2", "B", is_active=False),
        ],
    )
    use_case = ListExercisesUseCase(repository=repository)

    result = list_exercises(
        request=_build_request("GET", "/api/v1/exercises"),
        include_inactive=False,
        use_case=use_case,
        feature_flags=InMemoryFeatureFlags({"exercise_list_api_enabled": True}),
    )

    assert [item.id for item in result] == ["1"]


def test_get_exercise_returns_404_when_missing() -> None:
    repository = InMemoryExerciseRepository(saved=[])
    use_case = GetExerciseUseCase(repository=repository)

    with pytest.raises(HTTPException) as error_info:
        get_exercise(
            exercise_id="missing",
            request=_build_request("GET", "/api/v1/exercises/missing"),
            use_case=use_case,
            feature_flags=InMemoryFeatureFlags({"exercise_get_api_enabled": True}),
        )

    assert error_info.value.status_code == 404


def test_update_exercise_updates_fields() -> None:
    repository = InMemoryExerciseRepository(saved=[_exercise("1", "Serve Drill")])
    use_case = UpdateExerciseUseCase(
        repository=repository,
        allowed_categories=ALLOWED_CATEGORIES,
    )

    result = update_exercise(
        exercise_id="1",
        payload=UpdateExerciseRequest(
            name="Defense Drill",
            tags=["Team", "TEAM"],
            categories=["Difesa"],
        ),
        request=_build_request("PATCH", "/api/v1/exercises/1"),
        use_case=use_case,
        feature_flags=InMemoryFeatureFlags({"exercise_update_api_enabled": True}),
    )

    assert result.name == "Defense Drill"
    assert result.tags == ["team"]
    assert result.categories == ["difesa"]


def test_delete_exercise_soft_deletes() -> None:
    repository = InMemoryExerciseRepository(saved=[_exercise("1", "Serve Drill")])
    use_case = DeleteExerciseUseCase(repository=repository)

    delete_exercise(
        exercise_id="1",
        request=_build_request("DELETE", "/api/v1/exercises/1"),
        use_case=use_case,
        feature_flags=InMemoryFeatureFlags({"exercise_delete_api_enabled": True}),
    )

    assert repository.get_by_id("1", include_inactive=True) is not None
    assert repository.get_by_id("1") is None


def test_update_exercise_when_flag_disabled_returns_404() -> None:
    repository = InMemoryExerciseRepository(saved=[_exercise("1", "Serve Drill")])
    use_case = UpdateExerciseUseCase(
        repository=repository,
        allowed_categories=ALLOWED_CATEGORIES,
    )

    with pytest.raises(HTTPException) as error_info:
        update_exercise(
            exercise_id="1",
            payload=UpdateExerciseRequest(name="Another"),
            request=_build_request("PATCH", "/api/v1/exercises/1"),
            use_case=use_case,
            feature_flags=InMemoryFeatureFlags({"exercise_update_api_enabled": False}),
        )

    assert error_info.value.status_code == 404
