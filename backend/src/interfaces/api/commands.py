from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from application.commands.dto import (
    CommandLogDto,
    CommandRequestDto,
)
from application.commands.service import (
    CommandRejectedError,
    CommandService,
)
from domain.commands.registry import (
    UnknownCommandTypeError,
)
from domain.commands.invoker import (
    CommandInvoker,
)
from infrastructure.adapters.actuators.factory import (
    build_actuator_port,
)
from infrastructure.db import get_db
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from infrastructure.persistence.command_log_repository import (
    CommandLogRepository,
)
from infrastructure.persistence.device_repository import (
    DeviceRepository,
)


router = APIRouter(
    prefix="/api/commands",
    tags=["commands"],
)


def get_command_service(
    db: Session = Depends(get_db),
) -> CommandService:
    return CommandService(
        device_repository=DeviceRepository(
            db
        ),
        state_repository=(
            ActuatorStateRepository(db)
        ),
        command_log_repository=(
            CommandLogRepository(db)
        ),
        port=build_actuator_port(db),
        invoker=CommandInvoker(),
    )


@router.post(
    "",
    response_model=CommandLogDto,
)
def execute_command(
    request: CommandRequestDto,
    service: CommandService = Depends(
        get_command_service
    ),
):
    try:
        entry = service.execute(
            command_type=request.command_type,
            device_id=request.device_id,
            payload=request.payload,
        )

        return CommandLogDto(
            id=entry.id,
            command_type=entry.command_type,
            device_id=entry.device_id,
            payload=entry.payload,
            status=entry.status,
            error_message=entry.error_message,
            created_at=entry.created_at,
        )

    except UnknownCommandTypeError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        ) from exc

    except LookupError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=str(exc),
        ) from exc

    except CommandRejectedError as exc:
        entry = exc.entry

        return JSONResponse(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            content=CommandLogDto(
                id=entry.id,
                command_type=entry.command_type,
                device_id=entry.device_id,
                payload=entry.payload,
                status=entry.status,
                error_message=(
                    entry.error_message
                ),
                created_at=entry.created_at,
            ).model_dump(
                mode="json"
            ),
        )


@router.get(
    "",
    response_model=list[CommandLogDto],
)
def list_commands(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    db: Session = Depends(get_db),
):
    repository = CommandLogRepository(
        db
    )

    entries = repository.list_recent(
        limit
    )

    return [
        CommandLogDto(
            id=entry.id,
            command_type=entry.command_type,
            device_id=entry.device_id,
            payload=entry.payload,
            status=entry.status,
            error_message=(
                entry.error_message
            ),
            created_at=entry.created_at,
        )
        for entry in entries
    ]