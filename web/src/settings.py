import os
from pathlib import Path
from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "db.sqlite3"


class TelegramBotSettings(BaseModel):
    token: str = ""


class SMSSettings(BaseModel):
    email: EmailStr = os.getenv("SMSAERO_EMAIL")
    api_key: str = os.getenv("SMSAERO_API_KEY")
    gate_urls: str = "@gate.smsaero.ru/v2/"
    signature: str = "TechConnect"
    

class SMTPSettings(BaseModel):
    from_address: EmailStr = os.getenv("EMAIL_ADDRESS")
    from_address_password: str = os.getenv("EMAIL_PASSWORD")
    port: int = 587
    server: str = "smtp.yandex.ru"


class DbSettings(BaseModel):
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    echo: bool = True


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15


class OTP(BaseModel):
    length: int = 6


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 5050
    debug: bool = False

    db: DbSettings = DbSettings()

    otp: OTP = OTP()

    smtp: SMTPSettings = SMTPSettings()
    
    sms: SMSSettings = SMSSettings()

    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()
