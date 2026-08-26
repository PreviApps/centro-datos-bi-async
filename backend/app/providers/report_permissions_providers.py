from fastapi import Depends
from app.external.acceso_seguro_v2.acceso_seguro_v2_api import AccesoSeguroService
from sqlalchemy.orm import Session

from app.repositories.reports_repository import ReportsRepository
from app.repositories.report_permissions_repository import ReportPermissionsRepository
from app.services.report_permissions_service import ReportPermissionsService
from app.core.database_client import get_db


def get_permissions_service(db: Session = Depends(get_db)) -> ReportPermissionsService:
    reports_repo = ReportsRepository(db)
    permissions_repo = ReportPermissionsRepository(db)
    sso_service = AccesoSeguroService()
    return ReportPermissionsService(reports_repo, permissions_repo, sso_service)