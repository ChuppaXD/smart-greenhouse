from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from application.actuators.dto import (
    ActuatorApplyRequestDto,
    ActuatorExecutionDto,
)
from application.actuators.service import (
    ActuatorService,
)
from domain.actuators.errors import (
    ActuatorPolicyViolationError,
)
from infrastructure.adapters.actuators.logging_decorator import (
    LoggingActuatorDecorator,
)
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeActuatorDecorator,
)
from infrastructure.adapters.actuators.simulation import (
    SimulationActuatorAdapter,
)
from infrastructure.db import get_db
from infrastructure.persistence.execution_log_repository import (
    ExecutionLogRepository,
)


router = APIRouter(
    prefix="/api/actuators",
    tags=["actuators"],
)


def get_actuator_service(
    db: Session = Depends(get_db),
) -> ActuatorService:
    execution_log = (
        ExecutionLogRepository(db)
    )

    simulation_adapter = (
        SimulationActuatorAdapter()
    )

    max_runtime = (
        MaxRunTimeActuatorDecorator(
            simulation_adapter,
            db,
        )
    )

    decorated_port = (
        LoggingActuatorDecorator(
            max_runtime,
            execution_log,
        )
    )

    return ActuatorService(
        port=decorated_port,
        execution_log=execution_log,
    )


@router.get(
    "/executions",
    response_model=list[
        ActuatorExecutionDto
    ],
)
def list_executions(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    service: ActuatorService = Depends(
        get_actuator_service
    ),
):
    return service.list_executions(
        limit
    )


@router.post(
    "/apply",
    status_code=(
        status.HTTP_204_NO_CONTENT
    ),
)
def apply_actuator(
    request: ActuatorApplyRequestDto,
    service: ActuatorService = Depends(
        get_actuator_service
    ),
):
    try:
        service.apply(
            device_id=request.device_id,
            command=request.command,
            payload=request.payload,
        )

    except ActuatorPolicyViolationError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=str(exc),
        ) from exc

    return None