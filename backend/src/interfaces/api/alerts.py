from datetime import datetime
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from application.alerts.dto import (
    AlertDto,
)
from infrastructure.db import get_db
from infrastructure.persistence.alert_repository import (
    AlertRepository,
)


router = APIRouter(
    prefix="/api/alerts",
    tags=["alerts"],
)


@router.get(
    "",
    response_model=list[AlertDto],
)
def list_alerts(
    status: str = Query(
        default="active",
    ),
    location_id: UUID | None = Query(
        default=None,
    ),
    zone_id: UUID | None = Query(
        default=None,
    ),
    since: datetime | None = Query(
        default=None,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    db: Session = Depends(get_db),
):
    if status not in {
        "active",
        "resolved",
        "all",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "status must be active, "
                "resolved, or all."
            ),
        )

    repository = AlertRepository(db)

    return repository.list_recent(
        status=status,
        location_id=location_id,
        zone_id=zone_id,
        since=since,
        limit=limit,
    )