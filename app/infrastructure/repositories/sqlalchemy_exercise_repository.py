from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.models.exercise import Exercise
from app.domain.repositories.exercise_repository import ExerciseRepository
from app.infrastructure.db.models import ExerciseModel


class SqlAlchemyExerciseRepository(ExerciseRepository):
    def __init__(self, db_session: Session) -> None:
        self._db_session = db_session

    def exists_by_name(self, name: str) -> bool:
        statement = select(ExerciseModel.id).where(
            func.lower(ExerciseModel.name) == name.lower(),
        )
        return self._db_session.execute(statement).scalar_one_or_none() is not None

    def create(self, exercise: Exercise) -> Exercise:
        exercise_model = ExerciseModel(
            id=exercise.id,
            name=exercise.name,
            description=exercise.description,
            tags=exercise.tags,
            is_active=exercise.is_active,
            created_at=exercise.created_at,
            updated_at=exercise.updated_at,
        )
        self._db_session.add(exercise_model)
        self._db_session.commit()
        self._db_session.refresh(exercise_model)
        return Exercise(
            id=exercise_model.id,
            name=exercise_model.name,
            description=exercise_model.description,
            tags=list(exercise_model.tags),
            is_active=exercise_model.is_active,
            created_at=exercise_model.created_at,
            updated_at=exercise_model.updated_at,
        )
