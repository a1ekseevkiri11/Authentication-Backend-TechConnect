import json
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
    Response,
    Request,
    status,
    HTTPException,
    Form,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services.auth import EmailAuthService, TelephoneAuthService, TelegramAuthService
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



# @template_auth_router.post("/login/email/")
# async def template_login(
#     background_tasks: BackgroundTasks,
#     username: str = Form(...),
#     password: str = Form(...),
# ):
#     register_data = auth_schemas.EmailRegisterRequest(
#         email=username,
#         password=password,
#     )
#     temp_user_id = await EmailAuthService.register(
#         register_data=register_data,
#         background_tasks=background_tasks,
#     )
    
    

@template_auth_router.get("/profile/")
async def templates_profile(
    request: Request,
    current_user: auth_schemas.User = Depends(UserService.get_me)
):
    current_user_data = auth_schemas.UserResponse(
        id=current_user.id,
        email=current_user.email,
        telephone=current_user.telephone,        
    )
    return templates.TemplateResponse(
        request,
        "profile.html",
        {"user": current_user_data.model_dump()},
    )



######### API #############

auth_router = APIRouter(tags=["Auth"], prefix="/auth")

# EMAIL
@auth_router.post(
    "/register/email/",
)
async def email_register(
    register_data: auth_schemas.EmailRegisterRequest,
    background_tasks: BackgroundTasks,
) -> int:
    return await EmailAuthService.register(
        register_data=register_data,
        background_tasks=background_tasks,
    )


@auth_router.post(
    "/otp/email/",
    status_code=status.HTTP_201_CREATED,
    response_model=auth_schemas.UserResponse,
)
async def email_otp(
    temp_user_db_id: int,
    code: str,
):
    return await EmailAuthService.otp(
        temp_user_db_id=temp_user_db_id, 
        code=code
    )


@auth_router.post("/login/email/", response_model=auth_schemas.Token)
async def email_login(
    response: Response,
    login_data: auth_schemas.EmailLoginRequest = Depends(),
):
    return await EmailAuthService.login(
        response=response, 
        login_data=login_data,
    )


# TELEGRAM
@auth_router.get("/attach/telegram/")
async def attach_telegram(
    id: int = Query(..., alias="id"),
    first_name: str = Query(..., alias="first_name"),
    last_name: str = Query(..., alias="last_name"),
    username: str = Query(..., alias="username"),
    photo_url: str = Query(..., alias="photo_url"),
    auth_date: int = Query(..., alias="auth_date"),
    hash: str = Query(..., alias="hash"),
    current_user: auth_schemas.User = Depends(UserService.get_me)
):
    #TODO проверить хэш через ключ на правильность данных
    telegram_request = auth_schemas.TelegramRequest(
        id=id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        photo_url=photo_url,
        auth_date=auth_date,
        hash=hash,
    )
    await TelegramAuthService.attach(
        telegram_request=telegram_request,
        current_user=current_user,
    )


# TELEPHONE
@auth_router.post(
    "/register/telephone/",
)
async def telephone_register(
    register_data: auth_schemas.TelephoneRegisterRequest,
    background_tasks: BackgroundTasks,
):
    return await TelephoneAuthService.register(
        register_data=register_data,
        background_tasks=background_tasks,
    )


@auth_router.get(
    "/user/me/",
    response_model=auth_schemas.UserResponse,
)
async def me(
    current_user: auth_schemas.User = Depends(UserService.get_me)
):
    return current_user
