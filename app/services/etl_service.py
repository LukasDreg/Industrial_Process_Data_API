import csv
from datetime import datetime, timezone
from io import StringIO

from sqlalchemy.orm import Session

from app.models.measurement import Measurement
from app.schemas.measurement import CsvImportResult
from app.services.measurement_service import MeasurementService


class CsvEtlService:
    """ETL service for importing machine measurements from CSV files."""

    REQUIRED_COLUMNS = {"machine_id", "temperature", "rpm", "tool_wear"}

    def __init__(self, db: Session) -> None:
        self.db = db

    def import_csv(self, csv_content: str) -> CsvImportResult:
        reader = csv.DictReader(StringIO(csv_content))
        if reader.fieldnames is None:
            return CsvImportResult(imported=0, failed=1, errors=["CSV file is empty or missing headers."])

        missing_columns = self.REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing_columns:
            return CsvImportResult(
                imported=0,
                failed=1,
                errors=[f"Missing required columns: {', '.join(sorted(missing_columns))}"],
            )

        imported = 0
        failed = 0
        errors: list[str] = []
        measurements: list[Measurement] = []

        for row_number, row in enumerate(reader, start=2):
            try:
                measurements.append(
                    Measurement(
                        machine_id=self._required_text(row, "machine_id"),
                        temperature=float(self._required_text(row, "temperature")),
                        rpm=float(self._required_text(row, "rpm")),
                        tool_wear=float(self._required_text(row, "tool_wear")),
                        timestamp=self._parse_timestamp(row.get("timestamp")),
                    )
                )
                imported += 1
            except (ValueError, TypeError) as exc:
                failed += 1
                errors.append(f"Row {row_number}: {exc}")

        MeasurementService(self.db).create_many(measurements)

        return CsvImportResult(imported=imported, failed=failed, errors=errors)

    @staticmethod
    def _required_text(row: dict[str, str | None], column: str) -> str:
        value = row.get(column)
        if value is None or value.strip() == "":
            raise ValueError(f"Column '{column}' is required")
        return value.strip()

    @staticmethod
    def _parse_timestamp(value: str | None) -> datetime:
        if value is None or value.strip() == "":
            return datetime.now(timezone.utc)
        normalized = value.strip().replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError("timestamp must be a valid ISO 8601 datetime") from exc