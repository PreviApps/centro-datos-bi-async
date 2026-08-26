from sqlalchemy.orm import Session
from app.models.board import BoardModel, PositionBoardPermission, UserBoardPermission
from app.api.schemas.board import BoardCreate, BoardUpdate

class BoardsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(BoardModel).all()

    def get_by_id(self, board_id: str):
        return self.db.query(BoardModel).filter(BoardModel.id == board_id).first()

    def create(self, data: BoardCreate):
        new_board = BoardModel(**data)
        self.db.add(new_board)
        self.db.commit()
        self.db.refresh(new_board)
        return new_board

    def update(self, board_id: str, data: BoardUpdate):
        board = self.get_by_id(board_id)
        if not board:
            return None
        if hasattr(data, "model_dump"):
            update_data = data.model_dump(exclude_unset=True)  # Pydantic v2
        elif hasattr(data, "dict"):
            update_data = data.dict(exclude_unset=True)        # Pydantic v1
        else:
            update_data = dict(data)                           # Si ya es un dict

        for key, value in update_data.items():
            setattr(board, key, value)
            
        self.db.commit()
        self.db.refresh(board)
        return board

    def delete(self, board_id: str):
        board = self.get_by_id(board_id)
        if board:
            self.db.delete(board)
            self.db.commit()
            return True
        return False

    def get_all_by_user_permissions(self, user_id: str, position_name: str = None):
        """
        Obtiene los tableros que tienen permiso explícito para este usuario 
        O para su cargo (position_name). Replicando la lógica de reportes.
        """
        # IDs de tableros permitidos explícitamente para el usuario
        user_board_ids = self.db.query(UserBoardPermission.board_id).filter(
            UserBoardPermission.user_id == user_id
        ).subquery()

        # IDs de tableros permitidos por el cargo del usuario (si aplica)
        position_board_ids = []
        if position_name:
            position_board_ids = self.db.query(PositionBoardPermission.board_id).filter(
                PositionBoardPermission.position_name == position_name
            ).subquery()

        # Consultar los tableros que coincidan con cualquiera de los dos criterios
        return self.db.query(BoardModel).filter(
            (BoardModel.id.in_(user_board_ids)) | 
            (BoardModel.id.in_(position_board_ids))
        ).distinct().all()