from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import get_settings
from app.core.exceptions import AuthenticationFailureException

settings = get_settings()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    print(f"API Key: {api_key}")
    if api_key == settings.API_KEY:
        return api_key
    raise AuthenticationFailureException()
