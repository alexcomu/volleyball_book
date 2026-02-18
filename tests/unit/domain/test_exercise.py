import pytest

from app.domain.models.exercise import (
    ExerciseFieldValidationError,
    normalize_exercise_fields,
)


def test_normalize_exercise_fields_trims_and_deduplicates_tags() -> None:
    normalized = normalize_exercise_fields(
        name="  Serve Receive Drill ",
        description="  Three pass rotation ",
        tags=["Serve", " serve ", "Team"],
    )

    assert normalized.name == "Serve Receive Drill"
    assert normalized.description == "Three pass rotation"
    assert normalized.tags == ["serve", "team"]


def test_normalize_exercise_fields_rejects_blank_name() -> None:
    with pytest.raises(ExerciseFieldValidationError):
        normalize_exercise_fields(
            name="   ",
            description="desc",
            tags=["serve"],
        )


def test_normalize_exercise_fields_accepts_missing_tags() -> None:
    normalized = normalize_exercise_fields(
        name="Warmup Drill",
        description="desc",
        tags=None,
    )

    assert normalized.tags == []
