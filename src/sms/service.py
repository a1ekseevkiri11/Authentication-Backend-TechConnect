from urllib.parse import urlencode
import aiohttp


from src.settings import settings


class SMSService:
    @staticmethod
    async def send_sms(telephone: str, msg: str):
        url = f"https://{settings.sms.email}:{settings.sms.api_key}@{settings.sms.gate_url}sms/send"

        params = {
            "number": telephone,
            "text": msg,
            "sign": settings.sms.signature,
        }
        full_url = f"{url}?{urlencode(params)}"
        print(full_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(full_url, timeout=settings.sms.timeout) as response:
                content = await response.json()
                
        print(content)
        if content.get("success"):
            print(f"SMS успешно отправлен на номер: {telephone}")
        else:
            print(f"Ошибка при отправке SMS: {content.get('message')}")
