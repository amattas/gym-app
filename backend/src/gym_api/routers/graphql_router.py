import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import PyJWTError
from strawberry.fastapi import GraphQLRouter

from gym_api.graphql.schema import schema
from gym_api.services.auth_service import decode_access_token

_scheme = HTTPBearer()


async def get_graphql_context(
    credentials: HTTPAuthorizationCredentials = Depends(_scheme),
):
    try:
        payload = decode_access_token(credentials.credentials)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return {
        "user_id": uuid.UUID(payload["sub"]),
        "gym_id": uuid.UUID(payload["gym_id"]) if payload.get("gym_id") else None,
    }


router = GraphQLRouter(
    schema,
    path="/v1/graphql",
    context_getter=get_graphql_context,
)
