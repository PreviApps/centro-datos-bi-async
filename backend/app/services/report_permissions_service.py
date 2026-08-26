from fastapi import HTTPException

from app.repositories.reports_repository import ReportsRepository
from app.repositories.report_permissions_repository import ReportPermissionsRepository
from app.external.acceso_seguro_v2.acceso_seguro_v2_api import AccesoSeguroService

class ReportPermissionsService:
    def __init__(self, reports_repo: ReportsRepository, permissions_repo: ReportPermissionsRepository, sso_service: AccesoSeguroService):
        self.reports_repo = reports_repo
        self.permissions_repo = permissions_repo
        self.sso_service = sso_service

    def _verify_report_exists(self, report_id: str):
        report = self.reports_repo.get_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Reporte no encontrado")
        return report

    def update_user_permissions(self, report_id: str, user_ids: list[str], granted_by: str):
        self._verify_report_exists(report_id)

        current_perms = self.permissions_repo.get_users_by_report(report_id)
        current_user_ids = {str(p.user_id) for p in current_perms}
        new_user_ids = {str(uid) for uid in user_ids}

        users_to_add = list(new_user_ids - current_user_ids)
        users_to_remove = list(current_user_ids - new_user_ids)

        # Inserción y eliminación masiva de una sola pasada
        if users_to_add:
            self.permissions_repo.add_user_permission(report_id, users_to_add, granted_by)

        if users_to_remove:
            self.permissions_repo.remove_user_permissions(report_id, users_to_remove)

        self.permissions_repo.commit()
        return {"success": True, "message": "Permisos de usuario actualizados correctamente"}

    
    def get_report_permissions(self, report_id: str):
        self._verify_report_exists(report_id)

        user_perms = self.permissions_repo.get_users_by_report(report_id)
        position_perms = self.permissions_repo.get_positions_by_report(report_id)

        return {
            "user_ids": [p.user_id for p in user_perms],
            "position_names": [p.position_name for p in position_perms]
        }

    def get_report_users_with_permissions(self, report_id: str):
        """
        Consulta todos los usuarios del SSO y los cruza con los permisos locales del reporte.
        """
        self._verify_report_exists(report_id)

        # 1. Obtener todos los usuarios del SSO real
        sso_users = self.sso_service.get_all_users()

        # 2. Obtener los IDs de usuarios con permisos directos en la BD local
        user_perms = self.permissions_repo.get_users_by_report(report_id)
        granted_user_ids = {p.user_id for p in user_perms}

        # 3. Mapear y unificar la estructura para el frontend
        result = []
        for user in sso_users:
            user_id = str(user.get("id"))
            result.append({
                "id": user_id,
                "name": f"{user.get('name', '')} {user.get('last_name', '')}".strip(),
                "collaborator_position_name": user.get("collaborator_position_name", "Sin cargo asignado"),
                "corporate_email": user.get("corporate_email") or user.get("principal_email"),
                "has_permission": user_id in granted_user_ids
            })

        return result