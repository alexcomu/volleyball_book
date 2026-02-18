from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.models.exercise import Exercise, normalize_exercise_fields
from app.domain.repositories.exercise_repository import ExerciseRepository


class DuplicateExerciseNameError(ValueError):
    pass


@dataclass(frozen=True)
class CreateExerciseCommand:
    name: str
    description: str | None
    tags: list[str] | None
    categories: list[str] | None


@dataclass
class CreateExerciseUseCase:
    repository: ExerciseRepository

    def execute(self, command: CreateExerciseCommand) -> Exercise:
        normalized = normalize_exercise_fields(
            name=command.name,
            description=command.description,
            tags=command.tags,
            categories=command.categories,
        )
        if self.repository.exists_by_name(normalized.name):
            raise DuplicateExerciseNameError(
                f"Exercise with name '{normalized.name}' already exists.",
            )

        now = datetime.now(tz=UTC)
        exercise = Exercise(
            id=str(uuid4()),
            name=normalized.name,
            description=normalized.description,
            tags=normalized.tags,
            categories=normalized.categories,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        return self.repository.create(exercise)
