from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from application.automation.service import (
    AutomationService,
)
from application.overview.dto import (
    LocationOverviewDto,
)
from application.overview.facade import (
    LocationOverviewFacade,
)
from infrastructure.db import get_db
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)
from infrastructure.persistence.overview_repository import (
    LocationOverviewRepository,
)


router = APIRouter(
    prefix="/api/locations",
    tags=["overview"],
)


def get_overview_facade(
    db: Session = Depends(get_db),
) -> LocationOverviewFacade:
    overview_repository = (
        LocationOverviewRepository(db)
    )

    automation_repository = (
        AutomationRepository(db)
    )

    automation_service = AutomationService(
        automation_repository
    )

    return LocationOverviewFacade(
        overview_repository=(
            overview_repository
        ),
        automation_repository=(
            automation_repository
        ),
        automation_service=(
            automation_service
        ),
    )


@router.get(
    "/{location_id}/overview",
    response_model=LocationOverviewDto,
)
def get_location_overview(
    location_id: UUID,
    facade: LocationOverviewFacade = Depends(
        get_overview_facade
    ),
):
    try:
        return facade.get_overview(
            location_id
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc