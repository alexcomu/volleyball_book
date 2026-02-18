from dataclasses import dataclass

import pytest
from fastapi import HTTPException, Request, Response
from pydantic import ValidationError

from app.api.routers.exercises import create_exercise
from app.api.schemas.exercise import CreateExerciseRequest
from app.application.use_cases.create_exercise import CreateExerciseUseCase
from app.domain.models.exercise import Exercise
from app.domain.repositories.exercise_repository import ExerciseRepository
from app.shared.feature_flags import InMemoryFeatureFlags


@dataclass
class InMemoryExerciseRepository(ExerciseRepository):
    saved: list[Exercise]

    def exists_by_name(self, name: str) -> bool:
        return any(item.name.lower() == name.strip().lower() for item in self.saved)

    def create(self, exercise: Exercise) -> Exercise:
        self.saved.append(exercise)
        return exercise


def _build_request() -> Request:
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/exercises",
            "headers": [],
        },
    )
    request.state.request_id = "test-request-id"
    return request


def test_create_exercise_returns_201_and_body() -> None:
    repository = InMemoryExerciseRepository(saved=[])
    use_case = CreateExerciseUseCase(repository=repository)

    payload = CreateExerciseRequest(
        name="  Serve Receive Drill ",
        description="Three pass receive rotation",
        tags=["Serve", " serve ", "Team"],
    )
    response = Response()
    result = create_exercise(
        payload=payload,
        request=_build_request(),
        response=response,
        use_case=use_case,
        feature_flags=InMemoryFeatureFlags({"exercise_create_api_enabled": True}),
    )

    assert result.name == "Serve Receive Drill"
    assert result.description == "Three pass receive rotation"
    assert result.tags == ["serve", "team"]
    assert result.is_active is True
    assert result.id
    assert result.created_at
    assert result.updated_at
    assert response.headers["X-Request-ID"] == "test-request-id"


def test_create_exercise_with_invalid_payload_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        CreateExerciseRequest(name="  ", description="invalid")


def test_create_exercise_with_duplicate_name_returns_409() -> None:
    repository = InMemoryExerciseRepository(saved=[])
    use_case = CreateExerciseUseCase(repository=repository)
    payload = CreateExerciseRequest(
        name="Serve Receive Drill",
        description="desc",
        tags=["serve"],
    )
    create_exercise(
        payload=payload,
        request=_build_request(),
        response=Response(),
        use_case=use_case,
        feature_flags=InMemoryFeatureFlags({"exercise_create_api_enabled": True}),
    )

    with pytest.raises(HTTPException) as error_info:
        create_exercise(
            payload=payload,
            request=_build_request(),
            response=Response(),
            use_case=use_case,
            feature_flags=InMemoryFeatureFlags({"exercise_create_api_enabled": True}),
        )

    assert error_info.value.status_code == 409


def test_create_exercise_when_flag_disabled_returns_404() -> None:
    repository = InMemoryExerciseRepository(saved=[])
    use_case = CreateExerciseUseCase(repository=repository)
    payload = CreateExerciseRequest(name="Serve Receive Drill", description="desc")

    with pytest.raises(HTTPException) as error_info:
        create_exercise(
            payload=payload,
            request=_build_request(),
            response=Response(),
            use_case=use_case,
            feature_flags=InMemoryFeatureFlags({"exercise_create_api_enabled": False}),
        )

    assert error_info.value.status_code == 404
