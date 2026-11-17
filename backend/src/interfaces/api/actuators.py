from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from application.actuators.dto import (
    ActuatorExecutionDto,
)
from application.actuators.service import (
    ActuatorService,
)
from infrastructure.adapters.actuators.factory import (
    build_actuator_port,
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

    return ActuatorService(
        port=build_actuator_port(db),
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