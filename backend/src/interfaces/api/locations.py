from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from application.devices.mappers import devices_to_dtos
from application.locations.config_service import (
    LocationConfigService,
)
from application.locations.dto import (
    BuildLocationConfigRequestDto,
    LocationConfigDto,
    LocationSummaryDto,
    ZoneCreateDto,
    ZoneResponseDto,
    ZoneUpdateDto,
)
from application.locations.zone_assignment_service import (
    ZoneAssignmentService,
)
from domain.locations.errors import ConfigurationError
from infrastructure.db import get_db
from infrastructure.persistence.device_repository import (
    DeviceRepository,
)
from infrastructure.persistence.location_repository import (
    LocationRepository,
)


router = APIRouter(
    prefix="/api/locations",
    tags=["locations"],
)


def get_location_service(
    db: Session = Depends(get_db),
) -> LocationConfigService:
    return LocationConfigService(
        LocationRepository(db)
    )


def get_zone_assignment_service(
    db: Session = Depends(get_db),
) -> ZoneAssignmentService:
    return ZoneAssignmentService(
        DeviceRepository(db)
    )


@router.post(
    "/config",
    response_model=LocationConfigDto,
    status_code=status.HTTP_201_CREATED,
)
def create_location_config(
    request: BuildLocationConfigRequestDto,
    service: LocationConfigService = Depends(
        get_location_service
    ),
):
    try:
        return service.build_and_save(request)

    except ConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[LocationSummaryDto],
    description="Returns all saved locations, newest first.",
)
def list_locations(
    service: LocationConfigService = Depends(
        get_location_service
    ),
):
    return service.list_locations()


@router.get(
    "/{location_id}/config",
    response_model=LocationConfigDto,
)
def get_location_config(
    location_id: UUID,
    service: LocationConfigService = Depends(
        get_location_service
    ),
):
    try:
        return service.get_config(location_id)

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_location(
    location_id: UUID,
    service: LocationConfigService = Depends(
        get_location_service
    ),
):
    try:
        service.delete_location(location_id)

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return None


@router.post(
    "/{location_id}/zones",
    response_model=ZoneResponseDto,
    status_code=status.HTTP_201_CREATED,
)
def add_zone(
    location_id: UUID,
    request: ZoneCreateDto,
    service: LocationConfigService = Depends(
        get_location_service
    ),
):
    try:
        return service.add_zone(
            location_id,
            request,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except (ConfigurationError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{location_id}/zones/{zone_id}",
    response_model=ZoneResponseDto,
)
def update_zone(
    location_id: UUID,
    zone_id: UUID,
    request: ZoneUpdateDto,
    service: LocationConfigService = Depends(
        get_location_service
    ),
):
    try:
        return service.update_zone(
            location_id,
            zone_id,
            request,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except (ConfigurationError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{location_id}/zones/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_zone(
    location_id: UUID,
    zone_id: UUID,
    service: LocationConfigService = Depends(
        get_location_service
    ),
):
    try:
        service.delete_zone(
            location_id,
            zone_id,
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except (ConfigurationError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return None


@router.get(
    "/{location_id}/zones/{zone_id}/devices",
)
def list_zone_devices(
    location_id: UUID,
    zone_id: UUID,
    service: ZoneAssignmentService = Depends(
        get_zone_assignment_service
    ),
):
    try:
        devices = service.list_devices(
            location_id,
            zone_id,
        )

        return devices_to_dtos(devices)

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc