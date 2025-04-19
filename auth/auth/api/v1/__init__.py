from fastapi import APIRouter

from auth.api.v1.login import router as login_router
from auth.api.v1.jwks import router as jwks_router

router = APIRouter()
router.include_router(login_router)
router.include_router(jwks_router)
