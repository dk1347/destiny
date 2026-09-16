from datetime import date, datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .calculation_profile import KR_STANDARD_V1, MIDNIGHT_V1
from .data_registry import DatasetError, RuleRegistry
from .four_pillars import four_pillars_for_datetime
from .saju_result import saju_result_for_date, saju_result_for_datetime
from .seun import seun_for_datetime
from .runtime_config import api_runtime_config

app = FastAPI(title="Destiny Calculation API")
_runtime_config = api_runtime_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_runtime_config.allowed_origins,
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


class CalculationRequest(BaseModel):
    birth_local_datetime: datetime | None = None
    birth_local_date: date | None = None
    calculation_profile_id: str = KR_STANDARD_V1.profile_id


class SeunRequest(BaseModel):
    birth_local_datetime: datetime
    target_local_datetime: datetime
    calculation_profile_id: str = KR_STANDARD_V1.profile_id


def _require_kst(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(hours=9):
        raise HTTPException(422, {"code": "INVALID_LOCAL_DATETIME", "message": f"Use an Asia/Seoul UTC+09:00 {field_name}."})


def _profile_for(profile_id: str):
    profiles = {KR_STANDARD_V1.profile_id: KR_STANDARD_V1, MIDNIGHT_V1.profile_id: MIDNIGHT_V1}
    profile = profiles.get(profile_id)
    if profile is None:
        raise HTTPException(422, {"code": "UNKNOWN_CALCULATION_PROFILE", "message": "Unsupported calculation profile."})
    return profile


@app.post("/v1/saju/calculate")
def calculate(request: CalculationRequest) -> dict[str, object]:
    profile = _profile_for(request.calculation_profile_id)
    try:
        if request.birth_local_datetime is not None and request.birth_local_date is None:
            _require_kst(request.birth_local_datetime, "datetime")
            return saju_result_for_datetime(request.birth_local_datetime, RuleRegistry(), profile).as_dict()
        if request.birth_local_date is not None and request.birth_local_datetime is None:
            return saju_result_for_date(request.birth_local_date, RuleRegistry()).as_dict()
        raise HTTPException(422, {"code": "INVALID_BIRTH_INPUT", "message": "Provide either a local date or a local datetime."})
    except ValueError as error:
        raise HTTPException(422, {"code": "BIRTH_TIME_NEEDED", "message": str(error)}) from error
    except DatasetError as error:
        raise HTTPException(503, {"code": error.code.value, "message": "Verified calculation data is unavailable."}) from error


@app.post("/v1/seun/calculate")
def calculate_seun(request: SeunRequest) -> dict[str, object]:
    """Return an annual pillar and structural relations for one target instant."""

    _require_kst(request.birth_local_datetime, "birth datetime")
    _require_kst(request.target_local_datetime, "target datetime")
    profile = _profile_for(request.calculation_profile_id)
    try:
        registry = RuleRegistry()
        natal = four_pillars_for_datetime(request.birth_local_datetime, registry, profile)
        annual = seun_for_datetime(natal, request.target_local_datetime, registry, profile)
        return annual.as_dict()
    except DatasetError as error:
        raise HTTPException(503, {"code": error.code.value, "message": "Verified calculation data is unavailable."}) from error
