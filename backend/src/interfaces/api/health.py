from fastapi import APIRouter

from infrastructure.db import check_database


router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
def health_check():
    db_ok = check_database()

    if db_ok:
        return {
            "status": "ok",
            "db": "ok",
        }

    return {
        "status": "degraded",
        "db": "fail",
    }