from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from infrastructure.db import get_db
from infrastructure.persistence.device_repository import DeviceRepository
from application.sensors.service import SensorService


router = APIRouter(
    prefix="/api/sensors",
    tags=["sensors"],
)


class CreateSensorRequest(BaseModel):
    type: str
    display_name: str | None = None


class SensorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_type: str
    display_name: str
    default_config: dict


def get_sensor_service(
    db: Session = Depends(get_db),
) -> SensorService:
    repository = DeviceRepository(db)
    return SensorService(repository)


@router.get("", response_model=list[SensorResponse])
def list_sensors(
    service: SensorService = Depends(get_sensor_service),
):
    return service.list_sensors()


@router.post(
    "",
    response_model=SensorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sensor(
    request: CreateSensorRequest,
    service: SensorService = Depends(get_sensor_service),
):
    try:
        return service.create_sensor(
            sensor_type=request.type,
            display_name=request.display_name,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc