from fastapi import HTTPException
from app.repositories.boards_repository import BoardsRepository
from app.api.schemas.board import BoardCreate, BoardUpdate
from app.core.powerbi_client import PowerBIClient

class BoardsService:
    def __init__(self, repo: BoardsRepository):
        self.repo = repo
        self.powerbi_client = PowerBIClient()

    def get_board(self, board_id: str):
        board = self.repo.get_by_id(board_id)
        if not board:
            raise HTTPException(
                status_code=404,
                detail="Tablero no encontrado"
            )
        return board

    def get_boards(self):
        boards = self.repo.get_all()
        return [
            {
                "id": str(board.id),
                "name": board.name,
                "description": board.description,
                "powerbi_report_id": board.powerbi_report_id,
                "workspace_id": board.workspace_id,
                "embed_url": board.embed_url,
                "created_by": str(board.created_by),
                "created_at": board.created_at
            }
            for board in boards
        ]

    def get_boards_for_user(self, user_id: str, position_name: str = None):
        """
        Retorna la lista de tableros permitidos para un usuario y cargo.
        """
        boards = self.repo.get_all_by_user_permissions(user_id, position_name)
        return [
            {
                "id": str(board.id),
                "name": board.name,
                "description": board.description,
                "powerbi_report_id": board.powerbi_report_id,
                "workspace_id": board.workspace_id,
                "embed_url": board.embed_url,
                "created_by": str(board.created_by),
                "created_at": board.created_at
            }
            for board in boards
        ]

    def create_board(self, board: BoardCreate):
        return self.repo.create(board.model_dump())

    def update_board(self, board_id: str, board_data: BoardUpdate):
        self.get_board(board_id) # Valida que exista
        update_dict = board_data.model_dump(exclude_unset=True)
        updated_board = self.repo.update(board_id, update_dict)
        return updated_board

    def delete_board(self, board_id: str):
        self.get_board(board_id)
        deleted = self.repo.delete(board_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Tablero no encontrado"
            )
        return {"message": "Tablero eliminado exitosamente"}

    def verify_user_access(self, board_id: str, user_id: str, position_name: str) -> bool:
        board = self.get_board(board_id)
        permitted_boards = self.repo.get_all_by_user_permissions(user_id, position_name)
        
        permitted_ids = [str(b.id) for b in permitted_boards]
        if str(board.id) not in permitted_ids:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para acceder a este tablero"
            )
        return True

    def get_powerbi_workspaces(self):
        return self.powerbi_client.get_workspaces()

    def get_powerbi_reports(self, workspace_id: str):
        return self.powerbi_client.get_reports_by_workspace(workspace_id)

    def get_board_embed_info(self, board_id: str):
        """
        Obtiene los metadatos del tablero y solicita a Power BI el token de incrustación.
        """
        board = self.get_board(board_id)

        try:
            embed_data = self.powerbi_client.get_embed_token(
                workspace_id=board.workspace_id,
                report_id=board.powerbi_report_id
            )

            return {
                "id": str(board.id),
                "name": board.name,
                "description": board.description,
                "workspace_id": board.workspace_id,
                "powerbi_report_id": board.powerbi_report_id,
                "embed_url": board.embed_url,
                "embed_token": embed_data.get("token"),
                "expiration": embed_data.get("expiration")
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"No se pudo cargar la información de Power BI: {str(e)}"
            )