from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from ..services.jwt_token_provider import JwtTokenProvider
from ...domain.exceptions import ExpiredTokenException, InvalidTokenException

class JwtUser:
    """Objeto minimo que drf espera como request.user"""

    def __init__(self, user_id: str, role: str):
        self.id = user_id
        self.role = role
        self.is_athenticated = True

class JwtAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header.startswith("Bearer "):
            return None # Si no hay token, dejar pasar (permission_class decidira)
        
        token = auth_header.split(" ")[1]
        token_provider = JwtTokenProvider()

        try: 
            payload = token_provider.decode_access_token(token)
        except (ExpiredTokenException, InvalidTokenException) as e:
            raise AuthenticationFailed(str(e))
        
        user = JwtUser(user_id=payload["sub"], role=payload["role"])
        return (user, token)