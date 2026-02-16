from datetime import datetime, timezone, timedelta
from typing import Any
from uuid import UUID

import jwt
from django.conf import settings

from ...domain.services.token_provider import TokenProvider
from ...domain.exceptions import ExpiredTokenException, InvalidTokenException

class JwtTokenProvider(TokenProvider):

    def __init__(self):
        self.secret = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_lifetime = timedelta(minutes=30)
        self.refresh_token_lifetime = timedelta(days=7)
    
    def generate_access_token(self, user_id: UUID, role: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),   #subject = quien es
            "role": role,           #que permiso tiene
            "type": "access",       #tipo de token
            "iat": now,             # cuando se creo
            "exp": now + self.access_token_lifetime # cuando expira
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def generate_refresh_token(self, session_id: UUID) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "session_id": str(session_id),
            "type": "refresh",
            "iat": now,
            "exp": now + self.refresh_token_lifetime,
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def decode_access_token(self, token: str) -> dict[str, Any]:
        return self._decode(token, expected_type="access")
    
    def decode_refresh_token(self, token: str) -> dict[str, Any]:
        return self._decode(token, expected_type="refresh")
    
    def _decode(self, token: str, expected_type: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenException()
        except jwt.InvalidTokenError:
            raise InvalidTokenException()
        
        if payload.get("type") != expected_type:
            raise InvalidTokenException()
        
        return payload
        