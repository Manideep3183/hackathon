from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Verify the bearer token provided in the Authorization header.
    
    Args:
        credentials: HTTP authorization credentials containing the bearer token
        
    Returns:
        str: The verified token
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if credentials.credentials != settings.bearer_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials