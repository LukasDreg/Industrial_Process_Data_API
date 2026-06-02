from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MeasurementBase(BaseModel):
    machine_id: str = Field(..., min_length=1, max_length=100, examples=["MACHINE-001"])
    temperature: float = Field(..., ge=-50, le=250, examples=[72.5])
    rpm: float = Field(..., ge=0, le=50000, examples=[1450.0])
    tool_wear: float = Field(..., ge=0, le=100, examples=[12.7])
    timestamp: datetime | None = Field(default=None, examples=["2026-06-02T09:30:00Z"])

    @field_validator("machine_id")
    @classmethod
    def machine_id_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("machine_id must not be blank")
        return value


class ErrorResponse(BaseModel):
    error: str
    detail: str | list | dict


class MeasurementCreate(MeasurementBase):
    """Payload for creating a measurement."""


class MeasurementRead(MeasurementBase):
    """Measurement returned by the API."""

    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class MeasurementList(BaseModel):
    items: list[MeasurementRead]
    total: int


class CsvImportResult(BaseModel):
    imported: int
    failed: int
    errors: list[str]


class MetricSummary(BaseModel):
    min: float | None
    max: float | None
    average: float | None


class AnalysisSummary(BaseModel):
    temperature: MetricSummary
    rpm: MetricSummary
    tool_wear: MetricSummary