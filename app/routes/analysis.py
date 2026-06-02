from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.measurement import AnalysisSummary
from app.services.analysis_service import AnalysisService


router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get("/summary", response_model=AnalysisSummary)
def get_summary(db: Session = Depends(get_db)):
    return AnalysisService(db).summary()