from domain.locations.entity import Location, LocationConfig, Zone
from domain.locations.errors import ConfigurationError


def validate_zone_values(
    name: str,
    moisture_threshold_low: float,
    moisture_threshold_high: float,
) -> None:
    cleaned_name = name.strip()

    if not cleaned_name:
        raise ConfigurationError("Zone name is required.")

    if not 0.0 <= moisture_threshold_low <= 1.0:
        raise ConfigurationError(
            "Moisture threshold low must be between 0.0 and 1.0."
        )

    if not 0.0 <= moisture_threshold_high <= 1.0:
        raise ConfigurationError(
            "Moisture threshold high must be between 0.0 and 1.0."
        )

    if moisture_threshold_low >= moisture_threshold_high:
        raise ConfigurationError(
            "Moisture threshold low must be less than high."
        )


class LocationConfigBuilder:
    def __init__(self) -> None:
        self._location_name = ""
        self._zones: list[Zone] = []

    def with_location_name(
        self,
        name: str,
    ) -> "LocationConfigBuilder":
        self._location_name = name.strip()
        return self

    def add_zone(
        self,
        name: str,
        moisture_threshold_low: float,
        moisture_threshold_high: float,
        schedule: dict | None = None,
    ) -> "LocationConfigBuilder":
        cleaned_name = name.strip()

        validate_zone_values(
            cleaned_name,
            moisture_threshold_low,
            moisture_threshold_high,
        )

        self._zones.append(
            Zone(
                name=cleaned_name,
                moisture_threshold_low=moisture_threshold_low,
                moisture_threshold_high=moisture_threshold_high,
                schedule=dict(schedule or {}),
                id=None,
            )
        )

        return self

    def build(self) -> LocationConfig:
        if not self._location_name:
            raise ConfigurationError(
                "Location name is required."
            )

        if not self._zones:
            raise ConfigurationError(
                "At least one zone is required."
            )

        zone_names = [zone.name.casefold() for zone in self._zones]

        if len(zone_names) != len(set(zone_names)):
            raise ConfigurationError(
                "Zone names must be unique within a location."
            )

        for zone in self._zones:
            validate_zone_values(
                zone.name,
                zone.moisture_threshold_low,
                zone.moisture_threshold_high,
            )

        location = Location(
            name=self._location_name,
            zones=tuple(self._zones),
            id=None,
        )

        return LocationConfig(
            location=location,
        )