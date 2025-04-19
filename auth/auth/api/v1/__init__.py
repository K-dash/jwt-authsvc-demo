from fastapi import APIRouter

from auth.api.v1.login import router as login_router
from auth.api.v1.jwks import router as jwks_router
from auth.api.v1.refresh import router as refresh_router
from auth.api.v1.logout import router as logout_router

router = APIRouter()
router.include_router(login_router)
router.include_router(refresh_router)
router.include_router(logout_router)
router.include_router(jwks_router)
