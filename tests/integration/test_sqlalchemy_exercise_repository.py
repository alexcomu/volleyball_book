from datetime import UTC, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.models.exercise import Exercise
from app.infrastructure.db.models import Base, ExerciseModel
from app.infrastructure.repositories.sqlalchemy_exercise_repository import (
    SqlAlchemyExerciseRepository,
)


def test_sqlalchemy_exercise_repository_persists_exercise() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with session_factory() as db_session:
        repository = SqlAlchemyExerciseRepository(db_session=db_session)
        now = datetime.now(tz=UTC)
        exercise = Exercise(
            id="88d95cf2-c3a1-4540-abce-a69e7f320f3b",
            name="Serve Receive Drill",
            description="desc",
            tags=["serve", "team"],
            categories=["ricezione", "difesa"],
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        repository.create(exercise)
        db_session.commit()

        persisted = db_session.execute(
            select(ExerciseModel).where(ExerciseModel.id == exercise.id),
        ).scalar_one()

    assert persisted.name == "Serve Receive Drill"
    assert persisted.tags == ["serve", "team"]
    assert persisted.categories == ["ricezione", "difesa"]
    assert persisted.is_active is True
