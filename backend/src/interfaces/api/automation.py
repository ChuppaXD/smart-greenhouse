from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from application.automation.dto import (
    RecommendationDto,
    StrategySelectionDto,
    StrategyUpdateDto,
)
from application.automation.service import (
    AutomationService,
    StrategyNotConfiguredError,
)
from infrastructure.db import get_db
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)


router = APIRouter(
    prefix="/api/locations",
    tags=["automation"],
)


def get_automation_service(
    db: Session = Depends(get_db),
) -> AutomationService:
    return AutomationService(
        AutomationRepository(db)
    )


@router.put(
    "/{location_id}/automation",
    response_model=StrategySelectionDto,
)
def save_strategy(
    location_id: UUID,
    request: StrategyUpdateDto,
    service: AutomationService = Depends(
        get_automation_service
    ),
):
    try:
        return service.set_strategy(
            location_id=location_id,
            strategy_key=request.strategy_key,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        ) from exc


@router.post(
    "/{location_id}/automation/evaluate",
    response_model=RecommendationDto,
)
def evaluate_strategy(
    location_id: UUID,
    service: AutomationService = Depends(
        get_automation_service
    ),
):
    try:
        return service.evaluate(
            location_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc

    except StrategyNotConfiguredError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        ) from exc