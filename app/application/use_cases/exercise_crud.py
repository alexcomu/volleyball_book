from dataclasses import dataclass
from datetime import UTC, datetime

from app.application.use_cases.create_exercise import DuplicateExerciseNameError
from app.domain.models.exercise import Exercise, normalize_exercise_fields
from app.domain.repositories.exercise_repository import ExerciseRepository


class ExerciseNotFoundError(ValueError):
    pass


@dataclass
class ListExercisesUseCase:
    repository: ExerciseRepository

    def execute(self, include_inactive: bool = False) -> list[Exercise]:
        return self.repository.list(include_inactive=include_inactive)


@dataclass
class GetExerciseUseCase:
    repository: ExerciseRepository

    def execute(self, exercise_id: str) -> Exercise:
        exercise = self.repository.get_by_id(exercise_id=exercise_id)
        if exercise is None:
            raise ExerciseNotFoundError(f"Exercise '{exercise_id}' not found.")
        return exercise


@dataclass(frozen=True)
class UpdateExerciseCommand:
    exercise_id: str
    name: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    categories: list[str] | None = None
    name_provided: bool = False
    description_provided: bool = False
    tags_provided: bool = False
    categories_provided: bool = False


@dataclass
class UpdateExerciseUseCase:
    repository: ExerciseRepository
    allowed_categories: set[str]

    def execute(self, command: UpdateExerciseCommand) -> Exercise:
        existing = self.repository.get_by_id(exercise_id=command.exercise_id)
        if existing is None:
            raise ExerciseNotFoundError(f"Exercise '{command.exercise_id}' not found.")

        merged_name = command.name if command.name_provided else existing.name
        merged_description = (
            command.description
            if command.description_provided
            else existing.description
        )
        merged_tags = command.tags if command.tags_provided else existing.tags
        merged_categories = (
            command.categories if command.categories_provided else existing.categories
        )

        normalized = normalize_exercise_fields(
            name=merged_name or "",
            description=merged_description,
            tags=merged_tags,
            categories=merged_categories,
            allowed_categories=self.allowed_categories,
        )

        if self.repository.exists_by_name(
            normalized.name,
            exclude_id=existing.id,
        ):
            raise DuplicateExerciseNameError(
                f"Exercise with name '{normalized.name}' already exists.",
            )

        updated = Exercise(
            id=existing.id,
            name=normalized.name,
            description=normalized.description,
            tags=normalized.tags,
            categories=normalized.categories,
            is_active=existing.is_active,
            created_at=existing.created_at,
            updated_at=datetime.now(tz=UTC),
        )
        return self.repository.update(updated)


@dataclass
class DeleteExerciseUseCase:
    repository: ExerciseRepository

    def execute(self, exercise_id: str) -> None:
        existing = self.repository.get_by_id(exercise_id=exercise_id)
        if existing is None:
            raise ExerciseNotFoundError(f"Exercise '{exercise_id}' not found.")

        deleted = Exercise(
            id=existing.id,
            name=existing.name,
            description=existing.description,
            tags=existing.tags,
            categories=existing.categories,
            is_active=False,
            created_at=existing.created_at,
            updated_at=datetime.now(tz=UTC),
        )
        self.repository.update(deleted)
