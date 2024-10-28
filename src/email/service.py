import smtplib
from email.mime.text import MIMEText


from src.settings import settings


class EmailService:
    """
    Класс для отправки электронных писем через SMTP-сервер.

    Методы:
        send(to_address: str, msg: MIMEText) -> None
            Асинхронно отправляет электронное письмо указанному получателю с заданным сообщением.
    """
    @staticmethod
    async def send(to_adres: str, msg: MIMEText):
        """
        Отправляет электронное письмо через SMTP-сервер.

        Параметры:
        - to_address (str): Адрес получателя.
        - msg (MIMEText): Сообщение в формате MIMEText, содержащее текст письма.

        Метод использует настройки SMTP-сервера из settings, включая сервер, порт,
        адрес отправителя и пароль, чтобы установить соединение с сервером и
        отправить сообщение. Подключение шифруется с помощью TLS.

        Исключения:
        - Все исключения при отправке игнорируются.
        """
        try:
            with smtplib.SMTP(settings.smtp.server, settings.smtp.port) as server:
                server.starttls()
                server.login(
                    settings.smtp.from_address,
                    settings.smtp.from_address_password,
                )
                server.sendmail(settings.smtp.from_address, to_adres, msg.as_string())
        except Exception as e:
            pass
