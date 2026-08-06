from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.permission import UpdatePermissions
from app.providers.permissions_providers import get_permissions_service
from app.services.permissions_service import PermissionsService


router = APIRouter(
    prefix = "/reports"
)

@router.get("/{report_id}/users_with_permissions")
def get_report_users_with_permissions(
    report_id: str,
    service: PermissionsService = Depends(get_permissions_service)
):
    """
    Retorna la lista de usuarios del SSO cruzada con los permisos del reporte.
    """
    return service.get_report_users_with_permissions(report_id)

@router.put("/{report_id}/permissions")
def update_report_permissions(
    report_id: str,
    payload: UpdatePermissions,
    service: PermissionsService = Depends(get_permissions_service)
):
    return service.update_user_permissions(report_id, payload.user_ids, payload.admin_user_id)