from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.measurement import CsvImportResult
from app.services.etl_service import CsvEtlService


router = APIRouter(prefix="/etl", tags=["ETL"])


@router.post("/import-csv", response_model=CsvImportResult)
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import measurements from a CSV file into PostgreSQL.

    Expected columns: machine_id, temperature, rpm, tool_wear, timestamp(optional)
    """
    if file.content_type not in {"text/csv", "application/vnd.ms-excel", "application/octet-stream"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV uploads are supported.",
        )

    content = await file.read()
    try:
        csv_text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded.",
        ) from exc

    return CsvEtlService(db).import_csv(csv_text)