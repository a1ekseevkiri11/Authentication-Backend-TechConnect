from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request,
    status,
    HTTPException,
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/auth/templates")

auth_router = APIRouter(tags=["Auth"], prefix="/auth")

@auth_router.get(
    "/register/",
    response_class=HTMLResponse
)
async def register(
    request: Request
):
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
    request: Request
):
    return {"1": 1}

@auth_router.get("/login/", response_class=HTMLResponse)
async def get_login_form(
    request: Request
):
    return templates.TemplateResponse(
        "login.html", 
        {
            "request": request,
            "button_text": "Войти",
        },
    )

@auth_router.post("/login/")
async def login(
    request: Request
):
    return {"2": 2}
