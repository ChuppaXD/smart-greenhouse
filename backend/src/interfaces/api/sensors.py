from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from application.readings.dto import ReadingDto
from application.readings.service import (
    DeviceNotFoundError,
    ReadingIngest,
)
from application.sensors.service import SensorService
from infrastructure.adapters.sensors.selector import (
    SensorAdapterSelector,
)
from infrastructure.db import get_db
from infrastructure.persistence.device_repository import (
    DeviceRepository,
)
from infrastructure.persistence.reading_repository import (
    ReadingRepository,
)


router = APIRouter(
    prefix="/api/sensors",
    tags=["sensors"],
)


class CreateSensorRequest(BaseModel):
    type: str
    display_name: str | None = None


class SensorResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    device_type: str
    display_name: str
    default_config: dict
    sampling_interval_seconds: int
    tracking_enabled: bool


def get_sensor_service(
    db: Session = Depends(get_db),
) -> SensorService:
    return SensorService(
        DeviceRepository(db)
    )


def get_reading_ingest(
    db: Session = Depends(get_db),
) -> ReadingIngest:
    return ReadingIngest(
        device_repository=DeviceRepository(db),
        reading_repository=ReadingRepository(db),
        adapter_selector=SensorAdapterSelector(),
    )


@router.get(
    "",
    response_model=list[SensorResponse],
)
def list_sensors(
    service: SensorService = Depends(
        get_sensor_service
    ),
):
    return service.list_sensors()


@router.post(
    "",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sensor(
    request: CreateSensorRequest,
    service: SensorService = Depends(
        get_sensor_service
    ),
):
    try:
        return service.create_sensor(
            sensor_type=request.type,
            display_name=request.display_name,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        ) from exc


@router.post(
    "/{device_id}/read",
    response_model=ReadingDto,
)
def read_sensor(
    device_id: UUID,
    ingest: ReadingIngest = Depends(
        get_reading_ingest
    ),
):
    try:
        return ingest.take_reading(
            device_id
        )

    except DeviceNotFoundError as exc:
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


@router.get(
    "/{device_id}/readings",
    response_model=list[ReadingDto],
)
def list_sensor_readings(
    device_id: UUID,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    ingest: ReadingIngest = Depends(
        get_reading_ingest
    ),
):
    try:
        return ingest.list_readings(
            device_id,
            limit=limit,
        )

    except DeviceNotFoundError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc