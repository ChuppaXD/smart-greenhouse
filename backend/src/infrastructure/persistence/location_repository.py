from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from domain.locations.entity import LocationConfig
from infrastructure.persistence.models import (
    DeviceRow,
    LocationRow,
    ZoneRow,
)


class LocationRepository:
    def __init__(self, session: Session):
        self._session = session

    def save_config(
        self,
        config: LocationConfig,
    ) -> tuple[LocationRow, list[ZoneRow]]:
        try:
            location = LocationRow(
                name=config.location.name,
            )

            self._session.add(location)
            self._session.flush()

            zone_rows = [
                ZoneRow(
                    location_id=location.id,
                    name=zone.name,
                    moisture_threshold_low=zone.moisture_threshold_low,
                    moisture_threshold_high=zone.moisture_threshold_high,
                    schedule=zone.schedule,
                )
                for zone in config.location.zones
            ]

            self._session.add_all(zone_rows)
            self._session.commit()

            self._session.refresh(location)

            for zone in zone_rows:
                self._session.refresh(zone)

            return location, zone_rows

        except Exception:
            self._session.rollback()
            raise

    def list_locations(self) -> list[LocationRow]:
        statement = (
            select(LocationRow)
            .order_by(LocationRow.created_at.desc())
        )

        return list(
            self._session.execute(statement)
            .scalars()
            .all()
        )

    def get_location(
        self,
        location_id: UUID,
    ) -> LocationRow | None:
        return self._session.get(
            LocationRow,
            location_id,
        )

    def get_config(
        self,
        location_id: UUID,
    ) -> tuple[LocationRow, list[ZoneRow]] | None:
        location = self.get_location(location_id)

        if location is None:
            return None

        statement = (
            select(ZoneRow)
            .where(ZoneRow.location_id == location_id)
            .order_by(ZoneRow.name)
        )

        zones = list(
            self._session.execute(statement)
            .scalars()
            .all()
        )

        return location, zones

    def delete_location(
        self,
        location_id: UUID,
    ) -> bool:
        location = self.get_location(location_id)

        if location is None:
            return False

        try:
            self._session.execute(
                update(DeviceRow)
                .where(DeviceRow.location_id == location_id)
                .values(
                    zone_id=None,
                    location_id=None,
                )
            )

            self._session.delete(location)
            self._session.commit()

            return True

        except Exception:
            self._session.rollback()
            raise

    def zone_name_exists(
        self,
        location_id: UUID,
        name: str,
        exclude_zone_id: UUID | None = None,
    ) -> bool:
        statement = (
            select(ZoneRow.id)
            .where(
                ZoneRow.location_id == location_id,
                func.lower(ZoneRow.name) == name.casefold(),
            )
        )

        if exclude_zone_id is not None:
            statement = statement.where(
                ZoneRow.id != exclude_zone_id
            )

        return (
            self._session.execute(statement).first()
            is not None
        )

    def get_zone(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> ZoneRow | None:
        statement = (
            select(ZoneRow)
            .where(
                ZoneRow.id == zone_id,
                ZoneRow.location_id == location_id,
            )
        )

        return (
            self._session.execute(statement)
            .scalars()
            .first()
        )

    def count_zones(
        self,
        location_id: UUID,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(ZoneRow)
            .where(ZoneRow.location_id == location_id)
        )

        return int(
            self._session.execute(statement).scalar_one()
        )

    def add_zone(
        self,
        location_id: UUID,
        name: str,
        low: float,
        high: float,
        schedule: dict,
    ) -> ZoneRow:
        try:
            zone = ZoneRow(
                location_id=location_id,
                name=name,
                moisture_threshold_low=low,
                moisture_threshold_high=high,
                schedule=schedule,
            )

            self._session.add(zone)
            self._session.commit()
            self._session.refresh(zone)

            return zone

        except Exception:
            self._session.rollback()
            raise

    def update_zone(
        self,
        zone: ZoneRow,
        *,
        name: str,
        low: float,
        high: float,
        schedule: dict,
    ) -> ZoneRow:
        try:
            zone.name = name
            zone.moisture_threshold_low = low
            zone.moisture_threshold_high = high
            zone.schedule = schedule

            self._session.commit()
            self._session.refresh(zone)

            return zone

        except Exception:
            self._session.rollback()
            raise

    def delete_zone(
        self,
        zone: ZoneRow,
    ) -> None:
        try:
            self._session.execute(
                update(DeviceRow)
                .where(DeviceRow.zone_id == zone.id)
                .values(
                    zone_id=None,
                    location_id=None,
                )
            )

            self._session.delete(zone)
            self._session.commit()

        except Exception:
            self._session.rollback()
            raise