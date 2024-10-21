from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles


from src.settings import settings
from src.auth import routers as auth_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="palka_dazzla_web",
    description="",
    debug=settings.debug,
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(auth_routers.auth_router, prefix="")