from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.models.auth import TokenResponse
from src.services.auth_service import refresh_JWT


router = APIRouter(prefix="/auth", tags=["Autenticación"])

bearer_scheme = HTTPBearer()

@router.post("/refresh", response_model=TokenResponse)
async def refresh(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    print(credentials.credentials)
    return refresh_JWT(credentials.credentials)