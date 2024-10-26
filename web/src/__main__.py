import uvicorn

from src.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        reload_dirs=["src"],
    )
