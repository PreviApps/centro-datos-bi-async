from uuid import UUID
from sqlalchemy.orm import Session
from app.models.board import UserBoardPermission, PositionBoardPermission

class BoardPermissionsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_users_by_board(self, board_id: str) -> list[UserBoardPermission]:
        return self.db.query(UserBoardPermission).filter(UserBoardPermission.board_id == board_id).all()

    def get_positions_by_board(self, board_id: str) -> list[PositionBoardPermission]:
        return self.db.query(PositionBoardPermission).filter(PositionBoardPermission.board_id == board_id).all()

    def add_user_permission(self, board_id: str, user_ids: list[str], granted_by: str):
        if not user_ids:
            return
        board_uuid = UUID(board_id) if isinstance(board_id, str) else board_id
        new_perms = [
            UserBoardPermission(
                user_id=uid,
                board_id=board_uuid,
                granted_by=granted_by
            )
            for uid in user_ids
        ]
        self.db.bulk_save_objects(new_perms)

    def remove_user_permissions(self, board_id: str, user_ids: list[str]):
        if not user_ids:
            return
        self.db.query(UserBoardPermission).filter(
            UserBoardPermission.board_id == board_id,
            UserBoardPermission.user_id.in_(user_ids)
        ).delete(synchronize_session=False)

    def commit(self):
        self.db.commit()