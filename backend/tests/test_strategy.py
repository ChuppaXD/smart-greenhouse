import pytest
from uuid import uuid4

from domain.automation.context import (
    LocationAutomationContext,
)
from domain.automation.strategy import (
    AggressiveMoistureStrategy,
    ConservativeMoistureStrategy,
    get_strategy,
)


def make_context(
    moisture: float | None,
) -> LocationAutomationContext:
    return LocationAutomationContext(
        location_id=uuid4(),
        zone_id=uuid4(),
        moisture=moisture,
        low=0.25,
        high=0.45,
        light=None,
        zone_name="Main bed",
    )


def test_conservative_waits_when_within_band():
    context = make_context(
        moisture=0.40
    )

    recommendation = (
        ConservativeMoistureStrategy()
        .decide(context)
    )

    assert (
        recommendation.action
        == "wait"
    )


def test_aggressive_differs_on_same_context():
    context = make_context(
        moisture=0.40
    )

    conservative = (
        ConservativeMoistureStrategy()
        .decide(context)
    )

    aggressive = (
        AggressiveMoistureStrategy()
        .decide(context)
    )

    assert (
        conservative.action
        == "wait"
    )

    assert (
        aggressive.action
        == "irrigate"
    )


def test_no_moisture_sensor_waits():
    context = make_context(
        moisture=None
    )

    recommendation = (
        ConservativeMoistureStrategy()
        .decide(context)
    )

    assert (
        recommendation.action
        == "wait"
    )

    assert (
        "No moisture sensor"
        in recommendation.reason
    )


def test_unknown_strategy_is_rejected():
    with pytest.raises(
        ValueError,
        match="Unknown strategy key",
    ):
        get_strategy(
            "something_else"
        )