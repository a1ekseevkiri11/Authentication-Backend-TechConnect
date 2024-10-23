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
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services.auth import AuthService
from src.auth import schemas as auth_schemas
from src.auth.services.user import UserService


templates = Jinja2Templates(directory="src/auth/templates")


template_auth_router = APIRouter(tags=["Auth"], prefix="/auth")


# @template_auth_router.get("/register/", response_class=HTMLResponse)
# async def template_register_form(request: Request):
#     return templates.TemplateResponse(
#         "register.html",
#         {
#             "request": request,
#             "button_text": "Регистрация",
#         },
#     )


# @template_auth_router.post(
#     "/register/",
# )
# async def template_register(
#     username: str = Form(...),
#     password: str = Form(...),
# ):
#     try:
#         register_data = auth_schemas.EmailRegisterRequest(
#             email=username,
#             hashed_password=password,
#         )
#     except ValueError as ex:
#         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{ex}")

#     return await EmailAuthMethodWithPassword.register(
#         register_data=register_data,
#     )


# @template_auth_router.get("/login/", response_class=HTMLResponse)
# async def template_login_form(request: Request):
#     return templates.TemplateResponse(
#         "login.html",
#         {
#             "request": request,
#             "button_text": "Войти",
#         },
#     )


# @template_auth_router.post("/login/")
# async def template_login(
#     username: str = Form(...),
#     password: str = Form(...),
# ):
#     login_data = auth_schemas.LoginRequest(
#         identifier=username,
#         password=password,
#     )
#     return await EmailAuthMethodWithPassword.login(
#         login_data=login_data,
#     )


######### API #############

auth_router = APIRouter(tags=["Auth"], prefix="/auth")


@auth_router.post(
    "/register/",
)
async def register(
    register_data: auth_schemas.RegisterWithPasswordRequest,
) -> int:
    return await AuthService.register(register_data=register_data)


@auth_router.post(
    "/otp/",
    status_code=status.HTTP_201_CREATED,
    response_model=auth_schemas.UserResponse,
)
async def register(
    temp_user_db_id: int,
    code: str,
):
    return await AuthService.otp(temp_user_db_id=temp_user_db_id, code=code)


@auth_router.post("/login/", response_model=auth_schemas.Token)
async def login(
    response: Response,
    login_data: auth_schemas.LoginRequest = Depends(),
):
    return await AuthService.login(response=response, login_data=login_data)


@auth_router.get(
    "/user/me/",
    response_model=auth_schemas.UserResponse,
)
async def me(user: auth_schemas.User = Depends(UserService.get_me)):
    return user
