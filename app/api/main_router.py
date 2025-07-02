from fastapi import APIRouter
from app.api.endpoints import folders, vectorize, ask

api_router = APIRouter()

api_router.include_router(folders.router)
api_router.include_router(vectorize.router)
api_router.include_router(ask.router) 