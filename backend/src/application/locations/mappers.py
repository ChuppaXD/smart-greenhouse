from application.locations.dto import (
    LocationConfigDto,
    LocationSummaryDto,
    ZoneResponseDto,
)
from domain.locations.entity import LocationConfig
from infrastructure.persistence.models import LocationRow, ZoneRow


def location_config_to_dto(
    location_row: LocationRow,
    zone_rows: list[ZoneRow],
) -> LocationConfigDto:
    return LocationConfigDto(
        location=LocationSummaryDto(
            id=location_row.id,
            name=location_row.name,
        ),
        zones=[
            ZoneResponseDto(
                id=zone.id,
                location_id=zone.location_id,
                name=zone.name,
                moisture_threshold_low=float(
                    zone.moisture_threshold_low
                ),
                moisture_threshold_high=float(
                    zone.moisture_threshold_high
                ),
                schedule=zone.schedule,
            )
            for zone in zone_rows
        ],
    )


def location_rows_to_dtos(
    locations: list[LocationRow],
) -> list[LocationSummaryDto]:
    return [
        LocationSummaryDto(
            id=location.id,
            name=location.name,
        )
        for location in locations
    ]


def zone_row_to_dto(zone: ZoneRow) -> ZoneResponseDto:
    return ZoneResponseDto(
        id=zone.id,
        location_id=zone.location_id,
        name=zone.name,
        moisture_threshold_low=float(
            zone.moisture_threshold_low
        ),
        moisture_threshold_high=float(
            zone.moisture_threshold_high
        ),
        schedule=zone.schedule,
    )