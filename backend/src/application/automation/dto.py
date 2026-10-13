from uuid import UUID

from pydantic import BaseModel


class StrategyUpdateDto(BaseModel):
    strategy_key: str


class StrategySelectionDto(BaseModel):
    location_id: UUID
    strategy_key: str


class RecommendationDto(BaseModel):
    location_id: UUID
    strategy_key: str
    action: str
    reason: str