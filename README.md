# Authentication Backend "TechConnect"  
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)

Сервис написан на фреймворке FastAPI с использованием ORM SQLAlchemy. 
Поддерживает регистрацию через email/номер телефона с отправкой otp email/sms, и авторизацию через email, номер телефона или телеграм.
Для авторизации через телеграм, необходимо привязать аккаунт телеграм к существующему пользователю.

## Настройка

### Установка зависимостей
Если не установлен пакетный менеджер [Poetry](https://python-poetry.org/), выполните команду:
```bash
pip install poetry
```
Необходимо создать и активировать виртуальное окружение:
```bash
poetry shell
```
Далее установите зависимости:
```bash
poetry install
```

### Переменные окружения и остальные настройки

Скопируйте содержимое файла ```.env.template``` в файл ```.env``` и заполните его:
```
cp .env.template .env
```
### Настройки для работы рассылок через email
В файле ```.env```
```
EMAIL_ADDRESS=
EMAIL_PASSWORD=
```
В файле ```src/settings.py```
```python
class SMTPSettings(BaseModel):
    from_address: EmailStr = os.getenv("EMAIL_ADDRESS")
    from_address_password: str = os.getenv("EMAIL_PASSWORD")
    port: int #= НЕОБХОДИМО ЗАПОЛНИТЬ
    server: str #= НЕОБХОДИМО ЗАПОЛНИТЬ
```

### Настройки для рассылок sms через API SMSAero
В файле ```.env```
```
SMSAERO_EMAIL=
SMSAERO_API_KEY=
```
В файле ```src/settings.py```
```python
class SMSSettings(BaseModel):
    email: EmailStr = os.getenv("SMSAERO_EMAIL")
    api_key: str = os.getenv("SMSAERO_API_KEY")
    gate_url: str = "gate.smsaero.ru/v2/"
    signature: str = "SMS Aero" # можно поменять 
    timeout: int = 10
```


### Настройки для авторизации через телеграм

Документация к виджету - https://core.telegram.org/widgets/login

Статья как интегрировать виджет на сайт - https://codex.so/telegram-auth 

В файле ```.env```
```
TELEGRAM_BOT_TOKEN=
```
В файле ```src/settings.py```
```python
DOMAIN_FOR_TELEGRAM_AUTH_WIDGET = "" # НЕОБХОДИМО ЗАПОЛНИТЬ

 # Настройка виджета телеграм для его привязки к акаунту
 # Путь к виджету src/auth/templates/profile 
class TelegramAuthWidgetSettings:
    login: str #= НЕОБХОДИМО ЗАПОЛНИТЬ
    attach_url: str = f"{DOMAIN_FOR_TELEGRAM_AUTH_WIDGET}/api/auth/attach/telegram"
    login_url: str = f"{DOMAIN_FOR_TELEGRAM_AUTH_WIDGET}/api/auth/login/telegram"

class TelegramBotSettings(BaseModel):
    token: str = os.getenv("TELEGRAM_BOT_TOKEN")    
```

### Генерация ключей для выпуска и проверки JWT
Для генерации ключей необходимо установить программу [OpenSSL](https://github.com/openssl/openssl) или воспользоваться другим удобным для вас способом.

Создать директорию ```certs``` и перейти в нее:
```bash
mkdir certs
cd ./certs
```
Сгенериповать приватный ключ:
```
openssl genrsa -out jwt-private.pem 2048
```
Сгенерировать публичный ключ:
```
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```

## Запуск
Для запуска введите команду:
```bash
python -m src.__main__
```
## Запуск через Docker
```bash
docker-compose up --build
```
Примечание: для последующих запусков, если не было изменений в файлах проекта, можно использовать команду без флага --build:
```bash
docker-compose up
```

# Для разработчиков
## Как проверить аутентификацию пользователя:
```python
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
## Интерактивная документация
SwagerUI - ```/docs```

ReDoc - ```/redoc```

## Пример фронтенда Jinja2, JS и Bootstrap

#### Форма входа 
```
/auth/login
```

#### Форма регистрации 
```
/auth/register
```

#### Профиль
```
/auth/profile
```

## Модели
<div align="center">
  <kbd>
    <img height="500" src="https://github.com/user-attachments/assets/628a09f3-e5f5-492a-8bd6-784a016ee76a">
  </kbd>
</div>
