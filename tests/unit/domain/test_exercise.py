import pytest

from app.domain.models.exercise import (
    ExerciseFieldValidationError,
    normalize_exercise_fields,
)

ALLOWED_CATEGORIES = {"warmup", "ricezione", "servizio", "rigiocata", "difesa"}


def test_normalize_exercise_fields_trims_and_deduplicates_tags() -> None:
    normalized = normalize_exercise_fields(
        name="  Serve Receive Drill ",
        description="  Three pass rotation ",
        tags=["Serve", " serve ", "Team"],
        categories=["Warmup", "warmup", "Difesa"],
        allowed_categories=ALLOWED_CATEGORIES,
    )

    assert normalized.name == "Serve Receive Drill"
    assert normalized.description == "Three pass rotation"
    assert normalized.tags == ["serve", "team"]
    assert normalized.categories == ["warmup", "difesa"]


def test_normalize_exercise_fields_rejects_blank_name() -> None:
    with pytest.raises(ExerciseFieldValidationError):
        normalize_exercise_fields(
            name="   ",
            description="desc",
            tags=["serve"],
            categories=["warmup"],
            allowed_categories=ALLOWED_CATEGORIES,
        )


def test_normalize_exercise_fields_accepts_missing_tags() -> None:
    normalized = normalize_exercise_fields(
        name="Warmup Drill",
        description="desc",
        tags=None,
        categories=["warmup"],
        allowed_categories=ALLOWED_CATEGORIES,
    )

    assert normalized.tags == []


def test_normalize_exercise_fields_rejects_missing_categories() -> None:
    with pytest.raises(ExerciseFieldValidationError):
        normalize_exercise_fields(
            name="Warmup Drill",
            description="desc",
            tags=["warmup"],
            categories=None,
            allowed_categories=ALLOWED_CATEGORIES,
        )


def test_normalize_exercise_fields_rejects_invalid_categories() -> None:
    with pytest.raises(ExerciseFieldValidationError):
        normalize_exercise_fields(
            name="Warmup Drill",
            description="desc",
            tags=["warmup"],
            categories=["invalid"],
            allowed_categories=ALLOWED_CATEGORIES,
        )
