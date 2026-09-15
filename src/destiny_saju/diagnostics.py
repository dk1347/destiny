from enum import StrEnum


class DiagnosticCode(StrEnum):
    DATASET_NOT_PRODUCTION_VERIFIED = "DATASET_NOT_PRODUCTION_VERIFIED"
    DATASET_STATUS_INVALID = "DATASET_STATUS_INVALID"
    DATASET_SCHEMA_INVALID = "DATASET_SCHEMA_INVALID"
    INVALID_STEM = "INVALID_STEM"
    INVALID_BRANCH = "INVALID_BRANCH"


class CalculationInputError(TypeError):
    def __init__(self, code: DiagnosticCode, message: str) -> None:
        super().__init__(f"{code.value}: {message}")
        self.code = code
