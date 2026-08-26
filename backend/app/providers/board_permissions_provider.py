from fastapi import Depends
from sqlalchemy.orm import Session

from app.external.acceso_seguro_v2.acceso_seguro_v2_api import AccesoSeguroService
from app.repositories.boards_repository import BoardsRepository
from app.repositories.board_permissions_repository import BoardPermissionsRepository
from app.services.board_permissions_service import BoardPermissionsService
from app.core.database_client import get_db


def get_board_permissions_service(db: Session = Depends(get_db)) -> BoardPermissionsService:
    boards_repo = BoardsRepository(db)
    permissions_repo = BoardPermissionsRepository(db)
    sso_service = AccesoSeguroService()
    return BoardPermissionsService(boards_repo, permissions_repo, sso_service)