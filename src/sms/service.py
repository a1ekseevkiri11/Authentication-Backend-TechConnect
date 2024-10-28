from urllib.parse import urlencode
import aiohttp


from src.settings import settings


class SMSService:
    """
    Класс для отправки SMS-сообщений через SMS-шлюз.

    Методы:
        send_sms(telephone: str, msg: str) -> None
            Асинхронно отправляет SMS-сообщение на указанный номер телефона с заданным текстом.
    """
    @staticmethod
    async def send_sms(telephone: str, msg: str) -> None:
        """
        Отправляет SMS-сообщение через указанный SMS-шлюз.

        Параметры:
        - telephone (str): Номер телефона получателя сообщения.
        - msg (str): Текст сообщения.

        Использует параметры конфигурации из settings для построения запроса к SMS API.
        Формирует URL с учётом телефона, текста сообщения и подписи, а также применяет
        настройки времени ожидания.

        Исключения:
        - Поднимает исключение, если запрос не был успешен или не удалось обработать ответ.
        """
        url = f"https://{settings.sms.email}:{settings.sms.api_key}@{settings.sms.gate_url}sms/send"

        params = {
            "number": telephone,
            "text": msg,
            "sign": settings.sms.signature,
        }
        full_url = f"{url}?{urlencode(params)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(full_url, timeout=settings.sms.timeout) as response:
                content = await response.json()
