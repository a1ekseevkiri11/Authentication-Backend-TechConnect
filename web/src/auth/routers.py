from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request,
    status,
    HTTPException,
    Form,
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services.auth import EmailAuthMethodWithPassword
from src.auth import schemas as auth_schemas
from src.database import async_session_maker


templates = Jinja2Templates(directory="src/auth/templates")


auth_router = APIRouter(tags=["Auth"], prefix="/auth")


@auth_router.get("/register/", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "button_text": "Регистрация",
        },
    )


@auth_router.post(
    "/register/",
)
async def register(
    username: str = Form(...),
    password: str = Form(...),
):
    register_data = auth_schemas.EmailRegisterRequest(
        identifier=username,
        hashed_password=password,
    )
    return await EmailAuthMethodWithPassword.register(
        register_data=register_data,
    )


@auth_router.get("/login/", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "button_text": "Войти",
        },
    )


@auth_router.post("/login/")
async def login(
    username: str = Form(...),
    password: str = Form(...),
):
    login_data = auth_schemas.LoginRequest(
        identifier=username,
        password=password,
    )
    return await EmailAuthMethodWithPassword.login(
        login_data=login_data,
    )
