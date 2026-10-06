import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from application.readings.sampler import (
    SimulationSampler,
)
from application.readings.service import (
    ReadingIngest,
)
from infrastructure.adapters.sensors.selector import (
    SensorAdapterSelector,
)
from infrastructure.db import (
    SessionLocal,
)
from infrastructure.persistence.device_repository import (
    DeviceRepository,
)
from infrastructure.persistence.reading_repository import (
    ReadingRepository,
)
from infrastructure.settings import settings
from interfaces.api.devices import (
    router as devices_router,
)
from interfaces.api.health import (
    router as health_router,
)
from interfaces.api.locations import (
    router as locations_router,
)
from interfaces.api.sensors import (
    router as sensors_router,
)


logger = logging.getLogger(__name__)


def run_sampler_once() -> None:
    db = SessionLocal()

    try:
        device_repository = DeviceRepository(
            db
        )

        reading_repository = ReadingRepository(
            db
        )

        ingest = ReadingIngest(
            device_repository=device_repository,
            reading_repository=reading_repository,
            adapter_selector=(
                SensorAdapterSelector()
            ),
        )

        sampler = SimulationSampler(
            device_repository=device_repository,
            reading_repository=reading_repository,
            reading_ingest=ingest,
        )

        sampler.run_once(
            datetime.now(timezone.utc)
        )

    finally:
        db.close()


async def sampler_loop() -> None:
    while True:
        try:
            await asyncio.to_thread(
                run_sampler_once
            )

        except Exception:
            logger.exception(
                "Simulation sampler failed"
            )

        await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    sampler_task = asyncio.create_task(
        sampler_loop()
    )

    try:
        yield

    finally:
        sampler_task.cancel()

        with suppress(
            asyncio.CancelledError
        ):
            await sampler_task


app = FastAPI(
    title="Smart Greenhouse API",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)


origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router
)

app.include_router(
    sensors_router
)

app.include_router(
    devices_router
)

app.include_router(
    locations_router
)


@app.get("/")
def root():
    return {
        "message": "Smart Greenhouse API",
        "api_reference": "/scalar",
        "openapi": "/openapi.json",
    }


@app.get(
    "/scalar",
    include_in_schema=False,
)
def scalar():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )