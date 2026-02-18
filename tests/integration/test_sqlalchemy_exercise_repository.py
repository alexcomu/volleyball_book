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


def test_sqlalchemy_exercise_repository_lists_active_only_by_default() -> None:
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
        active = Exercise(
            id="d1f82af8-8e36-4443-a77d-e07dd66a12f0",
            name="Active",
            description="desc",
            tags=[],
            categories=["warmup"],
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        inactive = Exercise(
            id="9a4c37ce-ec52-4f81-b9df-e334b31dad48",
            name="Inactive",
            description="desc",
            tags=[],
            categories=["warmup"],
            is_active=False,
            created_at=now,
            updated_at=now,
        )
        repository.create(active)
        repository.create(inactive)

        active_only = repository.list()
        including_inactive = repository.list(include_inactive=True)

    assert [item.id for item in active_only] == ["d1f82af8-8e36-4443-a77d-e07dd66a12f0"]
    assert len(including_inactive) == 2


def test_sqlalchemy_exercise_repository_updates_existing_exercise() -> None:
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
        original = Exercise(
            id="1de69f52-a0f5-4d8f-9681-c27444a91389",
            name="Serve Drill",
            description="desc",
            tags=["team"],
            categories=["warmup"],
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        repository.create(original)

        updated = Exercise(
            id=original.id,
            name="Defense Drill",
            description="updated",
            tags=["defense"],
            categories=["difesa"],
            is_active=False,
            created_at=original.created_at,
            updated_at=datetime.now(tz=UTC),
        )
        repository.update(updated)

        persisted = repository.get_by_id(original.id, include_inactive=True)

    assert persisted is not None
    assert persisted.name == "Defense Drill"
    assert persisted.is_active is False
