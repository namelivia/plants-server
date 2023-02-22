from typing import Optional
from app.user_info.user_info import UserInfo
from fastapi import APIRouter, Header
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users")


@router.get("/me")
async def get_current_user(x_pomerium_jwt_assertion: Optional[str] = Header(None)):
    try:
        data = UserInfo.get_current(x_pomerium_jwt_assertion)
        logger.info(f"Current user: {data}")
        return data
    except Exception as err:
        logger.error(f"User info could not be retrieved: {str(err)}")
