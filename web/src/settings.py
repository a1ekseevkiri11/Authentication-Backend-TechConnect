from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "db.sqlite3"


class DbSettings(BaseModel):
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    echo: bool = True


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15


class OTP(BaseModel):
    count_incorrect_attempts: int = 3
    expire_minutes: int = 1
    delay_second: int = 30


class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 10000
    debug: bool = False

    db: DbSettings = DbSettings()

    otp: OTP = OTP()


settings = Settings()
