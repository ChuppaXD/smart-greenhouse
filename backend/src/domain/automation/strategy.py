from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from domain.automation.context import (
    LocationAutomationContext,
)


@dataclass(frozen=True)
class Recommendation:
    action: Literal["irrigate", "wait"]
    reason: str
    score: float | None = None


class AutomationStrategy(ABC):
    key: str

    @abstractmethod
    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        ...


class ConservativeMoistureStrategy(
    AutomationStrategy
):
    key = "conservative"

    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        if context.moisture is None:
            return Recommendation(
                action="wait",
                reason=self._reason(
                    context,
                    "No moisture sensor in this zone",
                ),
            )

        if context.moisture < context.low:
            return Recommendation(
                action="irrigate",
                reason=self._reason(
                    context,
                    (
                        f"Moisture {context.moisture:.2f} "
                        f"is below the low threshold "
                        f"{context.low:.2f}"
                    ),
                ),
            )

        if context.moisture < context.high:
            return Recommendation(
                action="wait",
                reason=self._reason(
                    context,
                    (
                        f"Moisture {context.moisture:.2f} "
                        f"is within "
                        f"{context.low:.2f}–"
                        f"{context.high:.2f}"
                    ),
                ),
            )

        return Recommendation(
            action="wait",
            reason=self._reason(
                context,
                (
                    f"Moisture {context.moisture:.2f} "
                    f"is at or above the high threshold "
                    f"{context.high:.2f}"
                ),
            ),
        )

    @staticmethod
    def _reason(
        context: LocationAutomationContext,
        message: str,
    ) -> str:
        if context.zone_name:
            return (
                f"Zone '{context.zone_name}': "
                f"{message}"
            )

        return message


class AggressiveMoistureStrategy(
    AutomationStrategy
):
    key = "aggressive"

    def decide(
        self,
        context: LocationAutomationContext,
    ) -> Recommendation:
        if context.moisture is None:
            return Recommendation(
                action="wait",
                reason=self._reason(
                    context,
                    "No moisture sensor in this zone",
                ),
            )

        if context.moisture < context.high:
            return Recommendation(
                action="irrigate",
                reason=self._reason(
                    context,
                    (
                        f"Moisture {context.moisture:.2f} "
                        f"is below the high threshold "
                        f"{context.high:.2f}; "
                        "aggressive strategy irrigates sooner"
                    ),
                ),
            )

        return Recommendation(
            action="wait",
            reason=self._reason(
                context,
                (
                    f"Moisture {context.moisture:.2f} "
                    f"is at or above the high threshold "
                    f"{context.high:.2f}"
                ),
            ),
        )

    @staticmethod
    def _reason(
        context: LocationAutomationContext,
        message: str,
    ) -> str:
        if context.zone_name:
            return (
                f"Zone '{context.zone_name}': "
                f"{message}"
            )

        return message


_STRATEGIES: dict[
    str,
    AutomationStrategy,
] = {
    "conservative": ConservativeMoistureStrategy(),
    "aggressive": AggressiveMoistureStrategy(),
}


def get_strategy(
    key: str,
) -> AutomationStrategy:
    normalized = key.strip().lower()

    try:
        return _STRATEGIES[normalized]
    except KeyError as exc:
        raise ValueError(
            f"Unknown strategy key: {key}"
        ) from exc