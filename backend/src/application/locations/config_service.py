from uuid import UUID

from application.locations.dto import (
    BuildLocationConfigRequestDto,
    LocationConfigDto,
    LocationSummaryDto,
    ZoneCreateDto,
    ZoneResponseDto,
    ZoneUpdateDto,
)
from application.locations.mappers import (
    location_config_to_dto,
    location_rows_to_dtos,
    zone_row_to_dto,
)
from domain.locations.config_builder import (
    LocationConfigBuilder,
    validate_zone_values,
)
from domain.locations.errors import ConfigurationError
from infrastructure.persistence.location_repository import (
    LocationRepository,
)


class LocationConfigService:
    def __init__(
        self,
        repository: LocationRepository,
    ):
        self._repo = repository

    def build_and_save(
        self,
        request: BuildLocationConfigRequestDto,
    ) -> LocationConfigDto:
        builder = (
            LocationConfigBuilder()
            .with_location_name(request.location_name)
        )

        for zone in request.zones:
            builder.add_zone(
                name=zone.name,
                moisture_threshold_low=zone.moisture_threshold_low,
                moisture_threshold_high=zone.moisture_threshold_high,
                schedule=zone.schedule,
            )

        config = builder.build()

        location_row, zone_rows = self._repo.save_config(
            config
        )

        return location_config_to_dto(
            location_row,
            zone_rows,
        )

    def list_locations(
        self,
    ) -> list[LocationSummaryDto]:
        rows = self._repo.list_locations()

        return location_rows_to_dtos(rows)

    def get_config(
        self,
        location_id: UUID,
    ) -> LocationConfigDto:
        result = self._repo.get_config(location_id)

        if result is None:
            raise LookupError("Location not found.")

        location_row, zone_rows = result

        return location_config_to_dto(
            location_row,
            zone_rows,
        )

    def delete_location(
        self,
        location_id: UUID,
    ) -> None:
        deleted = self._repo.delete_location(
            location_id
        )

        if not deleted:
            raise LookupError("Location not found.")

    def add_zone(
        self,
        location_id: UUID,
        zone: ZoneCreateDto,
    ) -> ZoneResponseDto:
        location = self._repo.get_location(location_id)

        if location is None:
            raise LookupError("Location not found.")

        validate_zone_values(
            zone.name,
            zone.moisture_threshold_low,
            zone.moisture_threshold_high,
        )

        cleaned_name = zone.name.strip()

        if self._repo.zone_name_exists(
            location_id,
            cleaned_name,
        ):
            raise ConfigurationError(
                "Zone names must be unique within a location."
            )

        saved = self._repo.add_zone(
            location_id=location_id,
            name=cleaned_name,
            low=zone.moisture_threshold_low,
            high=zone.moisture_threshold_high,
            schedule=dict(zone.schedule or {}),
        )

        return zone_row_to_dto(saved)

    def update_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
        update: ZoneUpdateDto,
    ) -> ZoneResponseDto:
        zone = self._repo.get_zone(
            location_id,
            zone_id,
        )

        if zone is None:
            raise LookupError(
                "Zone not found in this location."
            )

        new_name = (
            update.name.strip()
            if update.name is not None
            else zone.name
        )

        new_low = (
            update.moisture_threshold_low
            if update.moisture_threshold_low is not None
            else float(zone.moisture_threshold_low)
        )

        new_high = (
            update.moisture_threshold_high
            if update.moisture_threshold_high is not None
            else float(zone.moisture_threshold_high)
        )

        new_schedule = (
            dict(update.schedule)
            if update.schedule is not None
            else zone.schedule
        )

        validate_zone_values(
            new_name,
            new_low,
            new_high,
        )

        if self._repo.zone_name_exists(
            location_id,
            new_name,
            exclude_zone_id=zone_id,
        ):
            raise ConfigurationError(
                "Zone names must be unique within a location."
            )

        saved = self._repo.update_zone(
            zone,
            name=new_name,
            low=new_low,
            high=new_high,
            schedule=new_schedule,
        )

        return zone_row_to_dto(saved)

    def delete_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> None:
        location = self._repo.get_location(location_id)

        if location is None:
            raise LookupError("Location not found.")

        zone = self._repo.get_zone(
            location_id,
            zone_id,
        )

        if zone is None:
            raise LookupError(
                "Zone not found in this location."
            )

        if self._repo.count_zones(location_id) <= 1:
            raise ConfigurationError(
                "A location must keep at least one zone."
            )

        self._repo.delete_zone(zone)