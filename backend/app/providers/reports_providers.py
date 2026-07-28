from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database_client import get_db
from app.repositories.reports_repository import ReportsRepository
from app.services.reports_service import ReportsService


def get_reports_service(
    db: Session = Depends(get_db)
) -> ReportsService:

    repo = ReportsRepository(db)

    return ReportsService(repo)