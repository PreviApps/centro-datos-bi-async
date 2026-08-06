from fastapi import Depends
from app.external.acceso_seguro_v2.acceso_seguro_v2_api import AccesoSeguroService
from sqlalchemy.orm import Session

from app.repositories.reports_repository import ReportsRepository
from app.repositories.permissions_repository import PermissionsRepository
from app.services.permissions_service import PermissionsService
from app.core.database_client import get_db


def get_permissions_service(db: Session = Depends(get_db)) -> PermissionsService:
    reports_repo = ReportsRepository(db)
    permissions_repo = PermissionsRepository(db)
    sso_service = AccesoSeguroService()
    return PermissionsService(reports_repo, permissions_repo, sso_service)