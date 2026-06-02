from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.measurement import ErrorResponse, MeasurementCreate, MeasurementList, MeasurementRead
from app.services.measurement_service import MeasurementService


not_found_response = {404: {"model": ErrorResponse, "description": "Measurement not found"}}

router = APIRouter(prefix="/measurements", tags=["Measurements"])


@router.post("", response_model=MeasurementRead, status_code=status.HTTP_201_CREATED)
def create_measurement(payload: MeasurementCreate, db: Session = Depends(get_db)):
    """Create a single machine process measurement."""
    return MeasurementService(db).create(payload)


@router.get("", response_model=MeasurementList)
def list_measurements(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List measurements with pagination."""
    items, total = MeasurementService(db).list(skip=skip, limit=limit)
    return MeasurementList(items=items, total=total)


@router.get("/{measurement_id}", response_model=MeasurementRead, responses=not_found_response)
def get_measurement(measurement_id: int, db: Session = Depends(get_db)):
    """Get a measurement by ID."""
    measurement = MeasurementService(db).get(measurement_id)
    if measurement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Measurement not found")
    return measurement


@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT, responses=not_found_response)
def delete_measurement(measurement_id: int, db: Session = Depends(get_db)):
    """Delete a measurement by ID."""
    deleted = MeasurementService(db).delete(measurement_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Measurement not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)