from uuid import UUID

from application.automation.dto import (
    RecommendationDto,
    StrategySelectionDto,
)
from domain.automation.strategy import (
    get_strategy,
)
from infrastructure.persistence.automation_repository import (
    AutomationRepository,
)


class StrategyNotConfiguredError(
    ValueError
):
    pass


class AutomationService:
    def __init__(
        self,
        repository: AutomationRepository,
    ):
        self._repository = repository

    def set_strategy(
        self,
        location_id: UUID,
        strategy_key: str,
    ) -> StrategySelectionDto:
        if not self._repository.location_exists(
            location_id
        ):
            raise LookupError(
                "Location not found."
            )

        normalized_key = (
            strategy_key.strip().lower()
        )

        # Validate before touching persistence.
        get_strategy(normalized_key)

        saved_key = (
            self._repository.save_strategy(
                location_id=location_id,
                strategy_key=normalized_key,
            )
        )

        return StrategySelectionDto(
            location_id=location_id,
            strategy_key=saved_key,
        )

    def evaluate(
        self,
        location_id: UUID,
    ) -> RecommendationDto:
        if not self._repository.location_exists(
            location_id
        ):
            raise LookupError(
                "Location not found."
            )

        strategy_key = (
            self._repository.get_strategy_key(
                location_id
            )
        )

        if strategy_key is None:
            raise StrategyNotConfiguredError(
                "No automation strategy is configured "
                "for this location."
            )

        strategy = get_strategy(
            strategy_key
        )

        contexts = (
            self._repository.get_zone_contexts(
                location_id
            )
        )

        if not contexts:
            raise ValueError(
                "Location has no zones to evaluate."
            )

        evaluations = [
            (
                context,
                strategy.decide(context),
            )
            for context in contexts
        ]

        irrigation = next(
            (
                pair
                for pair in evaluations
                if pair[1].action
                == "irrigate"
            ),
            None,
        )

        if irrigation is not None:
            context, recommendation = (
                irrigation
            )

            reason = recommendation.reason

            missing_sensor_zones = [
                evaluation_context.zone_name
                for evaluation_context, evaluation
                in evaluations
                if (
                    evaluation_context.moisture
                    is None
                )
            ]

            if missing_sensor_zones:
                reason += (
                    " Other zones without a moisture "
                    "sensor: "
                    + ", ".join(
                        missing_sensor_zones
                    )
                    + "."
                )

            return RecommendationDto(
                location_id=location_id,
                strategy_key=strategy_key,
                action=recommendation.action,
                reason=reason,
            )

        missing_sensor_zones = [
            context.zone_name
            for context, recommendation
            in evaluations
            if context.moisture is None
        ]

        if (
            missing_sensor_zones
            and len(missing_sensor_zones)
            == len(evaluations)
        ):
            reason = (
                "No moisture sensor is assigned "
                "to the evaluated zone(s): "
                + ", ".join(
                    missing_sensor_zones
                )
                + "."
            )

            return RecommendationDto(
                location_id=location_id,
                strategy_key=strategy_key,
                action="wait",
                reason=reason,
            )

        context, recommendation = (
            evaluations[0]
        )

        return RecommendationDto(
            location_id=location_id,
            strategy_key=strategy_key,
            action=recommendation.action,
            reason=recommendation.reason,
        )