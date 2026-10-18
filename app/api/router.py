from fastapi import APIRouter, Depends

from app.api.endpoints import payments
from app.deps import require_api_key

router = APIRouter(dependencies=[Depends(require_api_key)])
router.include_router(payments.router, tags=["payments"])
