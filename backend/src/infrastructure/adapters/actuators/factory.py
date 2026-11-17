from sqlalchemy.orm import Session

from domain.actuators.ports import ActuatorPort
from infrastructure.adapters.actuators.logging_decorator import (
    LoggingActuatorDecorator,
)
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeActuatorDecorator,
)
from infrastructure.adapters.actuators.simulation import (
    SimulationActuatorAdapter,
)
from infrastructure.persistence.execution_log_repository import (
    ExecutionLogRepository,
)


def build_actuator_port(
    db: Session,
) -> ActuatorPort:
    execution_log = ExecutionLogRepository(
        db
    )

    simulation_adapter = (
        SimulationActuatorAdapter()
    )

    max_runtime_decorator = (
        MaxRunTimeActuatorDecorator(
            simulation_adapter,
            db,
        )
    )

    return LoggingActuatorDecorator(
        max_runtime_decorator,
        execution_log,
    )