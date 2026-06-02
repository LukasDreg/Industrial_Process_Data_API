from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.measurement import Measurement
from app.schemas.measurement import AnalysisSummary, MetricSummary


class AnalysisService:
    """Business logic for analytical measurement queries."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def summary(self) -> AnalysisSummary:
        row = self.db.execute(
            select(
                func.min(Measurement.temperature),
                func.max(Measurement.temperature),
                func.avg(Measurement.temperature),
                func.min(Measurement.rpm),
                func.max(Measurement.rpm),
                func.avg(Measurement.rpm),
                func.min(Measurement.tool_wear),
                func.max(Measurement.tool_wear),
                func.avg(Measurement.tool_wear),
            )
        ).one()

        return AnalysisSummary(
            temperature=MetricSummary(min=row[0], max=row[1], average=row[2]),
            rpm=MetricSummary(min=row[3], max=row[4], average=row[5]),
            tool_wear=MetricSummary(min=row[6], max=row[7], average=row[8]),
        )