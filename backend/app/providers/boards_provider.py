from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database_client import get_db
from app.repositories.boards_repository import BoardsRepository
from app.services.boards_service import BoardsService


def get_boards_service(
    db: Session = Depends(get_db)
) -> BoardsService:

    repo = BoardsRepository(db)

    return BoardsService(repo)