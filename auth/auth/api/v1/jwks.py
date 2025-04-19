from fastapi import APIRouter
from auth.services.jwt import PUBLIC_JWK_DICT
from copy import deepcopy

router = APIRouter(tags=["jwks"])

@router.get("/.well-known/jwks.json")
def jwks():
    jwk_pub = deepcopy(PUBLIC_JWK_DICT)  # 直接書き換えを避ける
    jwk_pub.update({"kid": "202504-key", "use": "sig", "alg": "RS256"})
    return {"keys": [jwk_pub]}
