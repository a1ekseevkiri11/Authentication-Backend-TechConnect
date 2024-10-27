from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
    Response,
    Request,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


from src.auth.services.auth import (
    EmailAuthService,
    TelephoneAuthService,
    TelegramAuthService,
)
from src.auth import schemas as auth_schemas
from src.auth.services.user import UserService
from src.settings import settings
from src.auth.services.jwt import TokenService

templates = Jinja2Templates(directory="src/auth/templates")


template_auth_router = APIRouter(tags=["Templates"], prefix="/auth")


@template_auth_router.get("/register/", response_class=HTMLResponse)
async def template_register(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
        },
    )


@template_auth_router.get("/login/", response_class=HTMLResponse)
async def template_login(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "telegram_auth_widget": {
                "auth_url": settings.telegram_auth_widget.login_url,
                "login": settings.telegram_auth_widget.login,
            }
        },
    )


@template_auth_router.get("/profile/")
async def templates_profile(
    request: Request, current_user: auth_schemas.User = Depends(UserService.get_me)
):
    return templates.TemplateResponse(
        request,
        "profile.html",
        {
            "user": current_user.model_dump(),
            "telegram_auth_widget": {
                "auth_url": settings.telegram_auth_widget.attach_url,
                "login": settings.telegram_auth_widget.login,
            }
        },
    )


######### API #############

auth_router = APIRouter(tags=["Auth"], prefix="/auth")


# EMAIL
@auth_router.post(
    "/register/email/",
    response_model=auth_schemas.TempUserResponce,
)
async def email_register(
    register_data: auth_schemas.EmailRegisterRequest,
    background_tasks: BackgroundTasks,
) -> auth_schemas.TempUserResponce:
    temp_user_id = await EmailAuthService.register(
        register_data=register_data,
        background_tasks=background_tasks,
    )
    return auth_schemas.TempUserResponce(
        id=temp_user_id
    )


@auth_router.post(
    "/otp/email/",
    status_code=status.HTTP_201_CREATED,
)
async def otp_email(
    otp_data: auth_schemas.OTPRequest
) -> None:
    await EmailAuthService.otp(
        temp_user_id=otp_data.temp_user_id, 
        code=otp_data.code
    )


@auth_router.post("/login/email/", response_model=auth_schemas.Token)
async def email_login(
    response: Response,
    login_data: auth_schemas.EmailLoginRequest,
):
    return await EmailAuthService.login(
        response=response,
        login_data=login_data,
    )


# TELEGRAM
@auth_router.get(
    "/attach/telegram/",
    response_class= RedirectResponse,
)
async def attach_telegram(
    id: int = Query(..., alias="id"),
    first_name: str = Query(..., alias="first_name"),
    last_name: str = Query(..., alias="last_name"),
    username: str = Query(..., alias="username"),
    photo_url: str = Query(..., alias="photo_url"),
    auth_date: int = Query(..., alias="auth_date"),
    hash: str = Query(..., alias="hash"),
    current_user: auth_schemas.User = Depends(UserService.get_me),
):
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
    return "/auth/profile/"


@auth_router.get(
    "/login/telegram/", 
    response_class= RedirectResponse,
)
async def telegram_login(
    response: Response,
    id: int = Query(..., alias="id"),
    first_name: str = Query(..., alias="first_name"),
    last_name: str = Query(..., alias="last_name"),
    username: str = Query(..., alias="username"),
    photo_url: str = Query(..., alias="photo_url"),
    auth_date: int = Query(..., alias="auth_date"),
    hash: str = Query(..., alias="hash"),
):
    telegram_request = auth_schemas.TelegramRequest(
        id=id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        photo_url=photo_url,
        auth_date=auth_date,
        hash=hash,
    )
    await TelegramAuthService.login(
        response=response,
        telegram_request=telegram_request,
    )
    return "/auth/profile/"
    


# TELEPHONE
@auth_router.post(
    "/register/telephone/",
    response_model=auth_schemas.TempUserResponce,
)
async def telephone_register(
    register_data: auth_schemas.TelephoneRegisterRequest,
    background_tasks: BackgroundTasks,
) -> auth_schemas.TempUserResponce:
    temp_user_id = await TelephoneAuthService.register(
        register_data=register_data,
        background_tasks=background_tasks,
    )
    return auth_schemas.TempUserResponce(
        id=temp_user_id
    )
    

@auth_router.post(
    "/otp/telephone/",
    status_code=status.HTTP_201_CREATED,
)
async def otp_telephone(
    otp_data: auth_schemas.OTPRequest
) -> None:
    await TelephoneAuthService.otp(
        temp_user_id=otp_data.temp_user_id, 
        code=otp_data.code
    )


@auth_router.post("/login/telephone/", response_model=auth_schemas.Token)
async def telephone_login(
    response: Response,
    login_data: auth_schemas.TelephoneLoginRequest,
):
    return await TelephoneAuthService.login(
        response=response,
        login_data=login_data,
    )


@auth_router.post(
    "/logout/",
)
async def logout(
    response: Response,
    current_user: auth_schemas.User = Depends(UserService.get_me)
) -> None:
    TokenService.clear(response)
    


# TODO перенести роутеры и методы user в отдельную директорию
@auth_router.get(
    "/user/me/",
    response_model=auth_schemas.UserResponse,
)
async def me(current_user: auth_schemas.User = Depends(UserService.get_me)):
    return current_user
