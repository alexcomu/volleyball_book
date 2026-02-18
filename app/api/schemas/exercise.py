from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CreateExerciseRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    tags: list[str] | None = None

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


class ExerciseResponse(BaseModel):
    id: str
    name: str
    description: str | None
    tags: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
