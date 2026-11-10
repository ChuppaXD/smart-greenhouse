from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ActuatorApplyRequestDto(
    BaseModel
):
    device_id: UUID
    command: str
    payload: dict = Field(
        default_factory=dict
    )


class ActuatorExecutionDto(
    BaseModel
):
    id: UUID
    device_id: UUID
    success: bool
    policy_applied: list[str]
    message: str | None
    created_at: datetime