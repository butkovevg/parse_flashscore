from fastapi import APIRouter

from .analysis import router as analysis_router
# from .favicon import router as favicon_router
from .favorites import router as favorites_router
from .graphql import router as graphql_router
from .tennis import router as tennis_router

router = APIRouter()
router.include_router(analysis_router)
router.include_router(favorites_router)
router.include_router(graphql_router)
router.include_router(tennis_router)
# router.include_router(favicon_router)
