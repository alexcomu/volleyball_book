from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.use_cases.create_exercise import CreateExerciseUseCase
from app.infrastructure.db.session import get_db_session as db_session_dependency
from app.infrastructure.repositories.sqlalchemy_exercise_repository import (
    SqlAlchemyExerciseRepository,
)
from app.shared.config import get_allowed_exercise_categories
from app.shared.feature_flags import FeatureFlags, InMemoryFeatureFlags


def get_db_session() -> Generator[Session]:
    yield from db_session_dependency()


def get_feature_flags() -> FeatureFlags:
    return InMemoryFeatureFlags({"exercise_create_api_enabled": True})


def get_create_exercise_use_case(
    db_session: Session = Depends(get_db_session),
) -> CreateExerciseUseCase:
    repository = SqlAlchemyExerciseRepository(db_session=db_session)
    return CreateExerciseUseCase(
        repository=repository,
        allowed_categories=get_allowed_exercise_categories(),
    )
