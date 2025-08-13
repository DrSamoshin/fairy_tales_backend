import logging
import jwt
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.configs import settings


async def get_user_id_from_token(
    credential: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> UUID:
    token = credential.credentials
    try:
        payload = jwt.decode(
            token,
            settings.jwt_token.JWT_POINT_SECRET_KEY,
            algorithms=[settings.jwt_token.ALGORITHM],
        )
        user_id_str = payload.get("sub")
        logging.info(f"user_id: {user_id_str}")
        user_id = UUID(user_id_str)
    except Exception as error:
        raise HTTPException(status_code=401, detail=str(error))
    else:
        return user_id
