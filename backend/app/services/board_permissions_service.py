from fastapi import HTTPException

from app.repositories.boards_repository import BoardsRepository
from app.repositories.board_permissions_repository import BoardPermissionsRepository
from app.external.acceso_seguro_v2.acceso_seguro_v2_api import AccesoSeguroService

class BoardPermissionsService:
    def __init__(self, boards_repo: BoardsRepository, permissions_repo: BoardPermissionsRepository, sso_service: AccesoSeguroService):
        self.boards_repo = boards_repo
        self.permissions_repo = permissions_repo
        self.sso_service = sso_service

    def _verify_board_exists(self, board_id: str):
        board = self.boards_repo.get_by_id(board_id)
        if not board:
            raise HTTPException(status_code=404, detail="Tablero no encontrado")
        return board

    def update_user_permissions(self, board_id: str, user_ids: list[str], granted_by: str):
        self._verify_board_exists(board_id)

        current_perms = self.permissions_repo.get_users_by_board(board_id)
        current_user_ids = {str(p.user_id) for p in current_perms}
        new_user_ids = {str(uid) for uid in user_ids}

        users_to_add = list(new_user_ids - current_user_ids)
        users_to_remove = list(current_user_ids - new_user_ids)

        if users_to_add:
            self.permissions_repo.add_user_permission(board_id, users_to_add, granted_by)

        if users_to_remove:
            self.permissions_repo.remove_user_permissions(board_id, users_to_remove)

        self.permissions_repo.commit()
        return {"success": True, "message": "Permisos de usuario actualizados correctamente"}

    def get_board_permissions(self, board_id: str):
        self._verify_board_exists(board_id)

        user_perms = self.permissions_repo.get_users_by_board(board_id)
        position_perms = self.permissions_repo.get_positions_by_board(board_id)

        return {
            "user_ids": [p.user_id for p in user_perms],
            "position_names": [p.position_name for p in position_perms]
        }

    def get_board_users_with_permissions(self, board_id: str):
        """
        Consulta todos los usuarios del SSO y los cruza con los permisos locales del tablero.
        """
        self._verify_board_exists(board_id)

        # 1. Obtener todos los usuarios del SSO real
        sso_users = self.sso_service.get_all_users()

        # 2. Obtener los IDs de usuarios con permisos directos en la BD local
        user_perms = self.permissions_repo.get_users_by_board(board_id)
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