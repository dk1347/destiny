from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .calculation_profile import KR_STANDARD_V1, MIDNIGHT_V1
from .data_registry import DatasetError, RuleRegistry
from .saju_result import saju_result_for_datetime

app = FastAPI(title="Destiny Calculation API")


class CalculationRequest(BaseModel):
    birth_local_datetime: datetime
    calculation_profile_id: str = KR_STANDARD_V1.profile_id


@app.post("/v1/saju/calculate")
def calculate(request: CalculationRequest) -> dict[str, object]:
    if request.birth_local_datetime.tzinfo is None or request.birth_local_datetime.utcoffset() != timedelta(hours=9):
        raise HTTPException(422, {"code": "INVALID_LOCAL_DATETIME", "message": "Use an Asia/Seoul UTC+09:00 datetime."})
    profiles = {KR_STANDARD_V1.profile_id: KR_STANDARD_V1, MIDNIGHT_V1.profile_id: MIDNIGHT_V1}
    profile = profiles.get(request.calculation_profile_id)
    if profile is None:
        raise HTTPException(422, {"code": "UNKNOWN_CALCULATION_PROFILE", "message": "Unsupported calculation profile."})
    try:
        return saju_result_for_datetime(request.birth_local_datetime, RuleRegistry(), profile).as_dict()
    except DatasetError as error:
        raise HTTPException(503, {"code": error.code.value, "message": "Verified calculation data is unavailable."}) from error
