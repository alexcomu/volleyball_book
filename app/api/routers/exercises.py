from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.api.dependencies import get_create_exercise_use_case, get_feature_flags
from app.api.schemas.exercise import CreateExerciseRequest, ExerciseResponse
from app.application.use_cases.create_exercise import (
    CreateExerciseCommand,
    CreateExerciseUseCase,
    DuplicateExerciseNameError,
)
from app.domain.models.exercise import ExerciseFieldValidationError
from app.shared.feature_flags import FeatureFlags
from app.shared.logging import get_logger, log_event

router = APIRouter(prefix="/api/v1/exercises", tags=["Exercises"])
logger = get_logger()


@router.post("", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(
    payload: CreateExerciseRequest,
    request: Request,
    response: Response,
    use_case: CreateExerciseUseCase = Depends(get_create_exercise_use_case),
    feature_flags: FeatureFlags = Depends(get_feature_flags),
) -> ExerciseResponse:
    if not feature_flags.is_enabled("exercise_create_api_enabled"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    started_at = datetime.now(tz=UTC)
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        created = use_case.execute(
            CreateExerciseCommand(
                name=payload.name,
                description=payload.description,
                tags=payload.tags,
            ),
        )
        latency_ms = int((datetime.now(tz=UTC) - started_at).total_seconds() * 1000)
        log_event(
            logger,
            "exercise_created",
            request_id=request_id,
            exercise_id=created.id,
            route=str(request.url.path),
            latency_ms=latency_ms,
            status_code=201,
        )
        response.headers["X-Request-ID"] = request_id
        return ExerciseResponse(
            id=created.id,
            name=created.name,
            description=created.description,
            tags=created.tags,
            is_active=created.is_active,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )
    except DuplicateExerciseNameError as error:
        log_event(
            logger,
            "exercise_create_duplicate_name",
            request_id=request_id,
            route=str(request.url.path),
            status_code=409,
            error=str(error),
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        ) from error
    except ExerciseFieldValidationError as error:
        log_event(
            logger,
            "exercise_create_validation_error",
            request_id=request_id,
            route=str(request.url.path),
            status_code=422,
            error=str(error),
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
