from fastapi import APIRouter

from app.schemas.compare import CompareRequest, CompareResponse
from app.services.compare_service import compare_codes

router = APIRouter(prefix="/api")


@router.post("/compare", response_model=CompareResponse)
def compare(request: CompareRequest) -> CompareResponse:
    return compare_codes(request)
