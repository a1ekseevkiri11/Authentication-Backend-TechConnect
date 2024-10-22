from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash(word: str) -> str:
    return pwd_context.hash(word)


def is_matched_hash(word: str, hashed: str) -> bool:
    return pwd_context.verify(word, hashed)
