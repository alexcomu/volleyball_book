from dataclasses import dataclass
from datetime import datetime


class ExerciseFieldValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Exercise:
    id: str
    name: str
    description: str | None
    tags: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class NormalizedExerciseFields:
    name: str
    description: str | None
    tags: list[str]


def normalize_exercise_fields(
    name: str,
    description: str | None,
    tags: list[str] | None,
) -> NormalizedExerciseFields:
    normalized_name = name.strip()
    if not normalized_name:
        raise ExerciseFieldValidationError("Exercise name cannot be blank.")
    if len(normalized_name) > 120:
        raise ExerciseFieldValidationError("Exercise name must be at most 120 chars.")

    normalized_description: str | None = None
    if description is not None:
        description_value = description.strip()
        if len(description_value) > 2000:
            raise ExerciseFieldValidationError(
                "Exercise description must be at most 2000 chars.",
            )
        normalized_description = description_value or None

    normalized_tags: list[str] = []
    seen_tags: set[str] = set()
    for raw_tag in tags or []:
        tag = raw_tag.strip().lower()
        if not tag:
            raise ExerciseFieldValidationError("Tags cannot be blank.")
        if len(tag) > 40:
            raise ExerciseFieldValidationError("Tags must be at most 40 chars.")
        if tag not in seen_tags:
            normalized_tags.append(tag)
            seen_tags.add(tag)

    return NormalizedExerciseFields(
        name=normalized_name,
        description=normalized_description,
        tags=normalized_tags,
    )
