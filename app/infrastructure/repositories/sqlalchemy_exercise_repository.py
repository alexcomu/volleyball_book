from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.models.exercise import Exercise
from app.domain.repositories.exercise_repository import ExerciseRepository
from app.infrastructure.db.models import ExerciseModel


class SqlAlchemyExerciseRepository(ExerciseRepository):
    def __init__(self, db_session: Session) -> None:
        self._db_session = db_session

    @staticmethod
    def _to_entity(exercise_model: ExerciseModel) -> Exercise:
        return Exercise(
            id=exercise_model.id,
            name=exercise_model.name,
            description=exercise_model.description,
            tags=list(exercise_model.tags),
            categories=list(exercise_model.categories),
            is_active=exercise_model.is_active,
            created_at=exercise_model.created_at,
            updated_at=exercise_model.updated_at,
        )

    def exists_by_name(self, name: str, exclude_id: str | None = None) -> bool:
        statement = select(ExerciseModel.id).where(
            func.lower(ExerciseModel.name) == name.lower(),
        )
        if exclude_id is not None:
            statement = statement.where(ExerciseModel.id != exclude_id)
        return self._db_session.execute(statement).scalar_one_or_none() is not None

    def create(self, exercise: Exercise) -> Exercise:
        exercise_model = ExerciseModel(
            id=exercise.id,
            name=exercise.name,
            description=exercise.description,
            tags=exercise.tags,
            categories=exercise.categories,
            is_active=exercise.is_active,
            created_at=exercise.created_at,
            updated_at=exercise.updated_at,
        )
        self._db_session.add(exercise_model)
        self._db_session.commit()
        self._db_session.refresh(exercise_model)
        return self._to_entity(exercise_model)

    def list(self, include_inactive: bool = False) -> list[Exercise]:
        statement = select(ExerciseModel).order_by(ExerciseModel.created_at.desc())
        if not include_inactive:
            statement = statement.where(ExerciseModel.is_active.is_(True))
        rows = self._db_session.execute(statement).scalars().all()
        return [self._to_entity(row) for row in rows]

    def get_by_id(
        self,
        exercise_id: str,
        include_inactive: bool = False,
    ) -> Exercise | None:
        statement = select(ExerciseModel).where(ExerciseModel.id == exercise_id)
        if not include_inactive:
            statement = statement.where(ExerciseModel.is_active.is_(True))
        exercise_model = self._db_session.execute(statement).scalar_one_or_none()
        if exercise_model is None:
            return None
        return self._to_entity(exercise_model)

    def update(self, exercise: Exercise) -> Exercise:
        exercise_model = self._db_session.execute(
            select(ExerciseModel).where(ExerciseModel.id == exercise.id),
        ).scalar_one()
        exercise_model.name = exercise.name
        exercise_model.description = exercise.description
        exercise_model.tags = exercise.tags
        exercise_model.categories = exercise.categories
        exercise_model.is_active = exercise.is_active
        exercise_model.updated_at = exercise.updated_at
        self._db_session.commit()
        self._db_session.refresh(exercise_model)
        return self._to_entity(exercise_model)
