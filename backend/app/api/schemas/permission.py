from typing import List, Optional
from pydantic import BaseModel

class UpdatePermissions(BaseModel):
    user_ids: List[str]
    position_names: Optional[List[str]] = []
    admin_user_id: str