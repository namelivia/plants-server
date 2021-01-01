from typing import Optional
import jwt
import os
from jwt import PyJWKClient
from fastapi import (
    APIRouter,
    Header
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users"
)


@router.get("/me")
async def get_current_user(
    x_pomerium_jwt_assertion: Optional[str] = Header(None)
):
    url = os.environ['JWK_ENDPOINT']
    jwks_client = PyJWKClient(url)
    kid = '8c5de961e5c06ea1426afe5a48ba6f008c95be9d325481f2ae05e8353d4b3dc5'
    signing_key = jwks_client.get_signing_key_from_jwt(kid)
    decoded = jwt.decode(
        x_pomerium_jwt_assertion,
        signing_key.key,
        algorithms=["ES256"]
    )
    return decoded
