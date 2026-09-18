from datetime import date, datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .calculation_profile import KR_STANDARD_V1, MIDNIGHT_V1
from .data_registry import DatasetError, RuleRegistry
from .diagnostics import DiagnosticCode
from .four_pillars import four_pillars_for_datetime
from .saju_result import saju_result_for_date, saju_result_for_datetime
from .seun import seun_for_datetime
from .runtime_config import api_runtime_config


def _dataset_error_response(error: DatasetError) -> HTTPException:
    """Map a DatasetError to an HTTP 503 with a user-readable Korean message.

    SOLAR_TERM_DATA_UNAVAILABLE carries a year-specific message produced by
    solar_terms.py; all other dataset errors receive a generic fallback.
    """
    if error.code is DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE:
        # DatasetError.__str__ produces "CODE: message".
        raw = str(error)
        message = raw.split(": ", 1)[1] if ": " in raw else raw
    else:
        message = "검증된 계산 데이터를 현재 사용할 수 없어요."
    return HTTPException(503, {"code": error.code.value, "message": message})


app = FastAPI(title="Destiny Calculation API")
_runtime_config = api_runtime_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_runtime_config.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
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


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Provide a non-sensitive process liveness signal for deployment checks."""

    return {"status": "ok", "service": "destiny-saju"}


def _require_kst(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() != timedelta(hours=9):
        raise HTTPException(422, {"code": "INVALID_LOCAL_DATETIME", "message": f"{field_name}은 한국 표준시(UTC+09:00)로 입력해 주세요."})


def _profile_for(profile_id: str):
    profiles = {KR_STANDARD_V1.profile_id: KR_STANDARD_V1, MIDNIGHT_V1.profile_id: MIDNIGHT_V1}
    profile = profiles.get(profile_id)
    if profile is None:
        raise HTTPException(422, {"code": "UNKNOWN_CALCULATION_PROFILE", "message": "지원하지 않는 계산 기준이에요."})
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
        raise HTTPException(422, {"code": "INVALID_BIRTH_INPUT", "message": "출생일 또는 출생일시 중 하나만 입력해 주세요."})
    except DatasetError as error:
        # DatasetError is a ValueError subclass — must be caught before ValueError.
        raise _dataset_error_response(error) from error
    except ValueError as error:
        raise HTTPException(422, {"code": "BIRTH_TIME_NEEDED", "message": str(error)}) from error


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
        raise _dataset_error_response(error) from error
