from fastapi import APIRouter, Depends
from app.api.schemas.board import BoardCreate, BoardUpdate
from app.api.schemas.permission import UpdatePermissions
from app.providers.boards_provider import get_boards_service
from app.providers.board_permissions_provider import get_board_permissions_service
from app.services.boards_service import BoardsService
from app.services.board_permissions_service import BoardPermissionsService

router = APIRouter(
    prefix = "/boards",
    tags = ["Boards"]
)

# --- CRUD Y OPERACIONES DE TABLEROS ---

@router.get("/")
async def get_boards(service: BoardsService = Depends(get_boards_service)):
    return service.get_boards()

@router.get("/{board_id}")
async def board_detail(board_id: str, service: BoardsService = Depends(get_boards_service)):
    return service.get_board(board_id)

@router.get("/by_user/{user_id}")
async def get_my_boards(
    user_id: str, 
    position_name: str = None,
    service: BoardsService = Depends(get_boards_service)
):
    """
    Retorna solo los tableros a los que el usuario específico tiene permiso otorgado.
    """
    return service.get_boards_for_user(user_id, position_name)

@router.post("/save_board")
async def create_board(body: BoardCreate, service: BoardsService = Depends(get_boards_service)):
    return service.create_board(body)

@router.patch("/edit_board/{board_id}")
async def update_board(
    board_id: str, 
    body: BoardUpdate, 
    service: BoardsService = Depends(get_boards_service)
):
    return service.update_board(board_id, body)

@router.delete("/delete_board/{board_id}")
async def delete_board(
    board_id: str, 
    service: BoardsService = Depends(get_boards_service)
):
    return service.delete_board(board_id)

@router.get("/powerbi/workspaces")
async def list_workspaces(service: BoardsService = Depends(get_boards_service)):
    return service.get_powerbi_workspaces()

@router.get("/powerbi/workspaces/{workspace_id}/reports")
async def list_reports(workspace_id: str, service: BoardsService = Depends(get_boards_service)):
    return service.get_powerbi_reports(workspace_id)

# --- GESTIÓN DE PERMISOS PARA TABLEROS ---

@router.get("/{board_id}/users_with_permissions")
def get_board_users_with_permissions(
    board_id: str,
    service: BoardPermissionsService = Depends(get_board_permissions_service)
):
    """
    Retorna la lista de usuarios del SSO cruzada con los permisos del tablero.
    """
    return service.get_board_users_with_permissions(board_id)

@router.put("/{board_id}/permissions")
def update_board_permissions(
    board_id: str,
    payload: UpdatePermissions,
    service: BoardPermissionsService = Depends(get_board_permissions_service)
):
    return service.update_user_permissions(board_id, payload.user_ids, payload.admin_user_id)

@router.get("/{board_id}/embed")
async def get_board_embed(
    board_id: str,
    service: BoardsService = Depends(get_boards_service)
):
    """
    Retorna el Embed URL y el Embed Token de Power BI listo para renderizar en el frontend.
    """
    return service.get_board_embed_info(board_id)