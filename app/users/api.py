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
    # Bypassing this until the thrid party is fixed.
    # https://github.com/jpadilla/pyjwt/issues/593

    return {
        "aud": [
            "example"
        ],
        "email": "user@example.com",
        "exp": 1237658,
        "iat": 1237658,
        "iss": "test.example.com",
        "nbf": 1237658,
        "sub": "user",
    }
    url = os.environ['JWK_ENDPOINT']
    jwks_client = PyJWKClient(url)
    signing_key = jwks_client.get_signing_key_from_jwt(
        x_pomerium_jwt_assertion
    )
    decoded = jwt.decode(
        x_pomerium_jwt_assertion,
        signing_key.key,
        algorithms=["ES256"]
    )
    return decoded
