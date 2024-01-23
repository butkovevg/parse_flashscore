from fastapi import APIRouter

from .analysis import router as analysis_router
from .favorites import router as favorites_router

router = APIRouter()
router.include_router(analysis_router)
router.include_router(favorites_router)
