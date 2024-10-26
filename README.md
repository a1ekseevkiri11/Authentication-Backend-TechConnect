# Authentication Backend "TechConnect"  
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
[SQLAlchemy](https://www.sqlalchemy.org/)
[Pydantic](https://docs.pydantic.dev/latest/)



## Содержание

## Настройка

Если не установлен пакетный менеджер [Poetry](https://python-poetry.org/), выполните команду:
```
pip install poetry
```
Необходимо создать и активировать виртуальное окружение:
```
poetry shell
```
Далее установите зависимости:
```
poetry install
```
Скопируйте содержимое файла ```.env.template``` в файл ```.env``` и заполните его:
Настройки email рассылки:
```
EMAIL_ADDRESS
EMAIL_PASSWORD
```
Настройки для отправки sms с помощью API SMSAero:
```
SMSAERO_EMAIL=
SMSAERO_API_KEY=
```
Сгенерировать сертификаты для работы JWT токена (дописать!!!)

## Запуск
Для запуска сервера FastAPI введите команду:
```
python -m src.__main__
```
## Запуск Docker
```
docker-compose up --build
```
Примечание: для последующих запусков, если не было изменений в файлах проекта, можно использовать команду без флага --build:
```
docker-compose up
```

# Для разработчиков
## Как проверить аутентификацию пользователя:
```
# Роутер без проверки аутентификации
@app.get("/public/")
async def public() -> None:
  pass

# Роутер с проверкой аутентификации
@app.get("/protect/")
async def protect(
  current_user: auth_schemas.User = Depends(UserService.get_me)
) -> None:
  pass
``` 

## Состав приложений

## Логирование

## Модели
