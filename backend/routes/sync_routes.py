from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

DATA = {}


class SyncModel(BaseModel):
    user_id: str
    payload: dict


@router.post("/sync/up")
def sync_up(data: SyncModel):

    DATA[data.user_id] = {
        "payload": data.payload,
        "updated_at": datetime.utcnow().isoformat()
    }

    return {
        "status": "synced",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/sync/down/{user_id}")
def sync_down(user_id: str):

    return DATA.get(user_id, {
        "status": "no_data"
    })
