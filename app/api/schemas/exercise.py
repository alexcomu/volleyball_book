from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.models.exercise import ALLOWED_EXERCISE_CATEGORIES


class CreateExerciseRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    tags: list[str] | None = None
    categories: list[str] = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("name cannot be blank")
        return normalized_value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized_value = value.strip()
        return normalized_value or None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None

        normalized_tags: list[str] = []
        seen_tags: set[str] = set()
        for raw_tag in value:
            tag = raw_tag.strip().lower()
            if not tag:
                raise ValueError("tags cannot contain blank entries")
            if len(tag) > 40:
                raise ValueError("each tag must be at most 40 chars")
            if tag not in seen_tags:
                normalized_tags.append(tag)
                seen_tags.add(tag)
        return normalized_tags

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, value: list[str]) -> list[str]:
        normalized_categories: list[str] = []
        seen_categories: set[str] = set()

        for raw_category in value:
            category = raw_category.strip().lower()
            if not category:
                raise ValueError("categories cannot contain blank entries")
            if category not in ALLOWED_EXERCISE_CATEGORIES:
                raise ValueError(f"invalid category: {category}")
            if category not in seen_categories:
                normalized_categories.append(category)
                seen_categories.add(category)

        if not normalized_categories:
            raise ValueError("at least one category is required")

        return normalized_categories


class ExerciseResponse(BaseModel):
    id: str
    name: str
    description: str | None
    tags: list[str]
    categories: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
