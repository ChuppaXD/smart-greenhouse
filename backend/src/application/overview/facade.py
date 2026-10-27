from collections import defaultdict
from uuid import UUID

from application.automation.service import (
    AutomationService,
)
from application.locations.dto import (
    LocationSummaryDto,
)
from application.overview.dto import (
    DeviceCountsDto,
    LocationOverviewDto,
    OverviewDeviceDto,
    OverviewReadingDto,
    OverviewRecommendationDto,
    OverviewZoneDto,
)
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)
from infrastructure.persistence.overview_repository import (
    LocationOverviewRepository,
)


class LocationOverviewFacade:
    """
    One entry point over locations, assigned devices,
    readings and the saved strategy.

    The facade composes existing pieces. It does not
    implement Strategy or Adapter logic itself.
    """

    def __init__(
        self,
        overview_repository: LocationOverviewRepository,
        automation_repository: AutomationRepository,
        automation_service: AutomationService,
    ):
        self._overview_repository = (
            overview_repository
        )
        self._automation_repository = (
            automation_repository
        )
        self._automation_service = (
            automation_service
        )

    def get_overview(
        self,
        location_id: UUID,
    ) -> LocationOverviewDto:
        location = (
            self._overview_repository
            .get_location_with_zones(
                location_id
            )
        )

        if location is None:
            raise LookupError(
                f"Location {location_id} was not found."
            )

        devices = (
            self._overview_repository
            .list_assigned_devices(
                location_id
            )
        )

        device_ids = [
            device.id
            for device in devices
        ]

        latest = (
            self._overview_repository
            .latest_readings(
                device_ids
            )
        )

        devices_by_zone: dict[
            UUID,
            list[OverviewDeviceDto],
        ] = defaultdict(list)

        readings_by_zone: dict[
            UUID,
            list[OverviewReadingDto],
        ] = defaultdict(list)

        latest_by_device = {
            reading.device_id: reading
            for reading in latest
        }

        sensor_count = sum(
            1
            for device in devices
            if device.role == "sensor"
        )

        actuator_count = sum(
            1
            for device in devices
            if device.role == "actuator"
        )

        for device in devices:
            devices_by_zone[
                device.zone_id
            ].append(
                OverviewDeviceDto(
                    id=device.id,
                    device_type=(
                        device.device_type
                    ),
                    role=device.role,
                    display_name=(
                        device.display_name
                    ),
                )
            )

            reading = latest_by_device.get(
                device.id
            )

            if reading is not None:
                readings_by_zone[
                    device.zone_id
                ].append(
                    OverviewReadingDto(
                        device_id=(
                            reading.device_id
                        ),
                        value=reading.value,
                        unit=reading.unit,
                        recorded_at=(
                            reading.recorded_at
                        ),
                        tracking_enabled=(
                            device.tracking_enabled
                        ),
                        sampling_interval_seconds=(
                            device.sampling_interval_seconds
                        ),
                    )
                )

        zones: list[
            OverviewZoneDto
        ] = []

        for zone in sorted(
            location.zones,
            key=lambda item: item.name,
        ):
            zones.append(
                OverviewZoneDto(
                    id=zone.id,
                    name=zone.name,
                    moisture_threshold_low=(
                        zone.moisture_threshold_low
                    ),
                    moisture_threshold_high=(
                        zone.moisture_threshold_high
                    ),
                    devices=devices_by_zone.get(
                        zone.id,
                        [],
                    ),
                    latest_readings=(
                        readings_by_zone.get(
                            zone.id,
                            [],
                        )
                    ),
                )
            )

        strategy_key = (
            self._automation_repository
            .get_strategy_key(
                location_id
            )
        )

        last_recommendation = None

        if strategy_key is not None:
            result = (
                self._automation_service
                .evaluate(
                    location_id
                )
            )

            last_recommendation = (
                OverviewRecommendationDto(
                    action=result.action,
                    reason=result.reason,
                )
            )

        return LocationOverviewDto(
            location=LocationSummaryDto(
                id=location.id,
                name=location.name,
            ),
            device_counts=DeviceCountsDto(
                sensor=sensor_count,
                actuator=actuator_count,
            ),
            zones=zones,
            strategy_key=strategy_key,
            last_recommendation=(
                last_recommendation
            ),
        )