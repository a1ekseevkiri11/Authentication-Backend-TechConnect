import smtplib
from email.mime.text import MIMEText


from src.settings import settings


class EmailService:
    @staticmethod
    async def send(
        to_adres: str,
        msg: MIMEText
    ):
        try:
            with smtplib.SMTP(
                settings.smtp.server, 
                settings.smtp.port
            ) as server:
                server.starttls()
                server.login(
                    settings.smtp.from_address, 
                    settings.smtp.from_address_password,
                )
                server.sendmail(
                    settings.smtp.from_address, to_adres, msg.as_string()
                )
        except Exception as e:
            print(f"ошибка в email{e}")
      