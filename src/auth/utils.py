from passlib.context import CryptContext
from typing import Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi import status
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash(word: str) -> str:
    return pwd_context.hash(word)


def is_matched_hash(word: str, hashed: str) -> bool:
    return pwd_context.verify(word, hashed)


class OAuth2PasswordCookie(OAuth2):
    """
    Класс для реализации аутентификации OAuth2 с использованием JWT-токена,
    хранящегося в cookie.

    Параметры:
    - tokenUrl: str - URL для получения токена.
    - scheme_name: Optional[str] - Название схемы аутентификации (по умолчанию None).
    - scopes: Optional[Dict[str, str]] - Опциональные области доступа для токена (по умолчанию пустой словарь).
    - auto_error: bool - Если True, будет выдано исключение, если токен не найден (по умолчанию True).
    """
    
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        """
        Получает токен из cookie запроса.

        Параметры:
        - request: Request - HTTP-запрос, содержащий cookie.

        Возвращает:
        - Optional[str]: Токен, если он найден, иначе None.

        Исключения:
        - HTTPException: Если токен не найден и auto_error равно True.
        """
        
        token = request.cookies.get("access_token")

        if token is not None:
            return token
        elif self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        else:
            return None
