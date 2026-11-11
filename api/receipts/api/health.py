from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["meta"])


class Health(BaseModel):
    status: str


@router.get("/health", operation_id="getHealth")
def health() -> Health:
    return Health(status="ok")
