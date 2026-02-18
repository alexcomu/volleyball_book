from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.api.dependencies import (
    get_create_exercise_use_case,
    get_delete_exercise_use_case,
    get_feature_flags,
    get_get_exercise_use_case,
    get_list_exercises_use_case,
    get_update_exercise_use_case,
)
from app.api.schemas.exercise import (
    CreateExerciseRequest,
    ExerciseResponse,
    UpdateExerciseRequest,
)
from app.application.use_cases.create_exercise import (
    CreateExerciseCommand,
    CreateExerciseUseCase,
    DuplicateExerciseNameError,
)
from app.application.use_cases.exercise_crud import (
    DeleteExerciseUseCase,
    ExerciseNotFoundError,
    GetExerciseUseCase,
    ListExercisesUseCase,
    UpdateExerciseCommand,
    UpdateExerciseUseCase,
)
from app.domain.models.exercise import Exercise, ExerciseFieldValidationError
from app.shared.feature_flags import FeatureFlags
from app.shared.logging import get_logger, log_event

router = APIRouter(prefix="/api/v1/exercises", tags=["Exercises"])
logger = get_logger()


def _to_response(exercise: Exercise) -> ExerciseResponse:
    return ExerciseResponse(
        id=exercise.id,
        name=exercise.name,
        description=exercise.description,
        tags=exercise.tags,
        categories=exercise.categories,
        is_active=exercise.is_active,
        created_at=exercise.created_at,
        updated_at=exercise.updated_at,
    )


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
                categories=payload.categories,
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
        return _to_response(created)
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


@router.get("", response_model=list[ExerciseResponse])
def list_exercises(
    request: Request,
    include_inactive: bool = False,
    use_case: ListExercisesUseCase = Depends(get_list_exercises_use_case),
    feature_flags: FeatureFlags = Depends(get_feature_flags),
) -> list[ExerciseResponse]:
    if not feature_flags.is_enabled("exercise_list_api_enabled"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    started_at = datetime.now(tz=UTC)
    request_id = getattr(request.state, "request_id", "unknown")
    exercises = use_case.execute(include_inactive=include_inactive)
    latency_ms = int((datetime.now(tz=UTC) - started_at).total_seconds() * 1000)
    log_event(
        logger,
        "exercise_listed",
        request_id=request_id,
        route=str(request.url.path),
        latency_ms=latency_ms,
        status_code=200,
    )
    return [_to_response(exercise) for exercise in exercises]


@router.get("/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(
    exercise_id: str,
    request: Request,
    use_case: GetExerciseUseCase = Depends(get_get_exercise_use_case),
    feature_flags: FeatureFlags = Depends(get_feature_flags),
) -> ExerciseResponse:
    if not feature_flags.is_enabled("exercise_get_api_enabled"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    request_id = getattr(request.state, "request_id", "unknown")
    try:
        exercise = use_case.execute(exercise_id=exercise_id)
        log_event(
            logger,
            "exercise_retrieved",
            request_id=request_id,
            exercise_id=exercise_id,
            route=str(request.url.path),
            status_code=200,
        )
        return _to_response(exercise)
    except ExerciseNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error


@router.patch("/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(
    exercise_id: str,
    payload: UpdateExerciseRequest,
    request: Request,
    use_case: UpdateExerciseUseCase = Depends(get_update_exercise_use_case),
    feature_flags: FeatureFlags = Depends(get_feature_flags),
) -> ExerciseResponse:
    if not feature_flags.is_enabled("exercise_update_api_enabled"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    request_id = getattr(request.state, "request_id", "unknown")
    payload_data = payload.model_dump(exclude_unset=True)
    try:
        updated = use_case.execute(
            UpdateExerciseCommand(
                exercise_id=exercise_id,
                name=payload_data.get("name"),
                description=payload_data.get("description"),
                tags=payload_data.get("tags"),
                categories=payload_data.get("categories"),
                name_provided="name" in payload_data,
                description_provided="description" in payload_data,
                tags_provided="tags" in payload_data,
                categories_provided="categories" in payload_data,
            ),
        )
        log_event(
            logger,
            "exercise_updated",
            request_id=request_id,
            exercise_id=exercise_id,
            route=str(request.url.path),
            status_code=200,
        )
        return _to_response(updated)
    except ExerciseNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
    except DuplicateExerciseNameError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except ExerciseFieldValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: str,
    request: Request,
    use_case: DeleteExerciseUseCase = Depends(get_delete_exercise_use_case),
    feature_flags: FeatureFlags = Depends(get_feature_flags),
) -> None:
    if not feature_flags.is_enabled("exercise_delete_api_enabled"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    request_id = getattr(request.state, "request_id", "unknown")
    try:
        use_case.execute(exercise_id=exercise_id)
        log_event(
            logger,
            "exercise_deleted",
            request_id=request_id,
            exercise_id=exercise_id,
            route=str(request.url.path),
            status_code=204,
        )
    except ExerciseNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
