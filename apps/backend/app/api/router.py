from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.files import router as files_router
from app.api.routes.graph import router as graph_router
from app.api.routes.health import router as health_router
from app.api.routes.ingestions import router as ingestions_router
from app.api.routes.meta import router as meta_router
from app.api.routes.notes import router as notes_router
from app.api.routes.parse_jobs import router as parse_jobs_router
from app.api.routes.preview import router as preview_router
from app.api.routes.problems import router as problems_router
from app.api.routes.review import router as review_router
from app.api.routes.runtime_config import router as runtime_config_router
from app.api.routes.search import router as search_router
from app.api.routes.solve import router as solve_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(meta_router, prefix="/v1")
api_router.include_router(auth_router, prefix="/v1")
api_router.include_router(files_router, prefix="/v1")
api_router.include_router(graph_router, prefix="/v1")
api_router.include_router(ingestions_router, prefix="/v1")
api_router.include_router(problems_router, prefix="/v1")
api_router.include_router(notes_router, prefix="/v1")
api_router.include_router(parse_jobs_router, prefix="/v1")
api_router.include_router(preview_router, prefix="/v1")
api_router.include_router(review_router, prefix="/v1")
api_router.include_router(runtime_config_router, prefix="/v1")
api_router.include_router(dashboard_router, prefix="/v1")
api_router.include_router(solve_router, prefix="/v1")
api_router.include_router(search_router, prefix="/v1")
