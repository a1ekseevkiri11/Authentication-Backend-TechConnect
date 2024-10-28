from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles


from src.settings import settings
from src.auth import routers as auth_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Authentication-Backend-TechConnect",
    description="",
    debug=settings.debug,
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(router=auth_routers.template_auth_router, prefix="")
app.include_router(router=auth_routers.auth_router, prefix="/api")
