from typing import Literal
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from application.devices.dto import DeviceDto
from application.devices.family_service import (
    DeviceFamilyService,
)
from application.devices.mappers import devices_to_dtos
from application.locations.dto import (
    ZoneAssignmentRequestDto,
)
from application.locations.zone_assignment_service import (
    ZoneAssignmentService,
)
from domain.locations.errors import ConfigurationError
from infrastructure.db import get_db
from infrastructure.persistence.device_repository import (
    DeviceRepository,
)


router = APIRouter(
    prefix="/api/devices",
    tags=["devices"],
)


def get_device_family_service(
    db: Session = Depends(get_db),
) -> DeviceFamilyService:
    repository = DeviceRepository(db)

    return DeviceFamilyService(repository)


def get_zone_assignment_service(
    db: Session = Depends(get_db),
) -> ZoneAssignmentService:
    repository = DeviceRepository(db)

    return ZoneAssignmentService(repository)


@router.get(
    "",
    response_model=list[DeviceDto],
)
def list_devices(
    family: str | None = Query(default=None),
    role: Literal["sensor", "actuator"] | None = Query(
        default=None
    ),
    service: DeviceFamilyService = Depends(
        get_device_family_service
    ),
):
    devices = service.list_devices(
        device_family=family,
        role=role,
    )

    return devices_to_dtos(devices)


@router.post(
    "/provision",
    response_model=list[DeviceDto],
    status_code=status.HTTP_201_CREATED,
)
def provision_devices(
    family: str = Query(...),
    service: DeviceFamilyService = Depends(
        get_device_family_service
    ),
):
    try:
        devices = service.provision_family(family)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return devices_to_dtos(devices)


@router.patch(
    "/{device_id}/zone",
    status_code=status.HTTP_204_NO_CONTENT,
)
def assign_device_to_zone(
    device_id: UUID,
    request: ZoneAssignmentRequestDto,
    service: ZoneAssignmentService = Depends(
        get_zone_assignment_service
    ),
):
    try:
        service.assign(
            device_id,
            request.zone_id,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return None