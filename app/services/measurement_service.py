from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.measurement import Measurement
from app.schemas.measurement import MeasurementCreate


class MeasurementService:
    """Business logic for measurement CRUD operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: MeasurementCreate) -> Measurement:
        data = payload.model_dump()
        if data["timestamp"] is None:
            data["timestamp"] = datetime.now(timezone.utc)

        measurement = Measurement(**data)
        self.db.add(measurement)
        self.db.commit()
        self.db.refresh(measurement)
        return measurement

    def create_many(self, measurements: list[Measurement]) -> int:
        if not measurements:
            return 0

        self.db.add_all(measurements)
        self.db.commit()
        return len(measurements)

    def list(self, skip: int = 0, limit: int = 100) -> tuple[list[Measurement], int]:
        total = self.db.scalar(select(func.count()).select_from(Measurement)) or 0
        statement = (
            select(Measurement)
            .order_by(Measurement.timestamp.desc(), Measurement.id.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list(self.db.scalars(statement).all())
        return items, total

    def get(self, measurement_id: int) -> Measurement | None:
        return self.db.get(Measurement, measurement_id)

    def delete(self, measurement_id: int) -> bool:
        measurement = self.get(measurement_id)
        if measurement is None:
            return False

        self.db.delete(measurement)
        self.db.commit()
        return True