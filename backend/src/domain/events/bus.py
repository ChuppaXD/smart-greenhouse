import logging
from collections.abc import Callable


logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[
            type,
            list[Callable],
        ] = {}

    def subscribe(
        self,
        event_type: type,
        handler: Callable,
    ) -> None:
        self._subscribers.setdefault(
            event_type,
            [],
        ).append(handler)

    def publish(
        self,
        event: object,
    ) -> None:
        handlers = tuple(
            self._subscribers.get(
                type(event),
                [],
            )
        )

        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception(
                    "Subscriber failed for %s",
                    type(event).__name__,
                )