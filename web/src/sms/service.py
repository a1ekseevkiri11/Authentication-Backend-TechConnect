from typing import Union, List, Dict, Optional

import datetime
import logging
import time

from urllib.parse import urljoin, quote_plus

import aiohttp


class SmsAeroException(Exception):
    """Super class of all SmsAero Errors."""


class SmsAeroConnectionException(SmsAeroException):
    """A Connection error occurred."""


class SmsAeroNoMoneyException(SmsAeroException):
    """No money on the account."""


logger = logging.getLogger(__name__)


class SmsAero:

    # Default signature for the messages
    SIGNATURE = "Sms Aero"

    def __init__(
        self,
        email: str,
        api_key: str,
        signature: str = SIGNATURE,
        timeout: int = 10,
    ):
        """
        Initializes the SmsAero class.

        Parameters:
        email (str): The user's email.
        api_key (str): The user's API key. Should be 32 characters.
        signature (str, optional): The signature for the messages.
        timeout (int, optional): The timeout for the requests.
        allow_phone_validation (bool, optional): Whether to allow phone number validation.
        url_gate (str, optional): The gateway URL. For example, '@local.host/v2/'.
        test_mode (bool, optional): Whether to enable test mode.
        """
        self.__user = email
        self.__akey = api_key
        self.__sign = signature
        self.__sess = None
        self.__time = timeout

    async def init_session(self):
        """
        Asynchronously initializes an aiohttp.ClientSession with a custom User-Agent header.

        This method checks if an existing session is open and closes it before initializing a new session.
        It sets a custom User-Agent header for the session to identify the client in HTTP requests.
        """
        if self.__sess is None or self.__sess.closed:
            self.__sess = aiohttp.ClientSession(headers={"User-Agent": "SAPythonAsyncClient/3.0.0"})
            logging.debug("Initialized aiohttp.ClientSession")

    async def close_session(self, *_):
        """
        Asynchronously closes the aiohttp.ClientSession if it exists and is open.

        This method ensures that the ClientSession is properly closed before the object is destroyed or reused,
        preventing potential resource leaks. It checks if the session exists and is not already closed before
        attempting to close it.
        """
        if self.__sess and not self.__sess.closed:
            await self.__sess.close()
            logging.debug("Closed aiohttp.ClientSession")


    @staticmethod
    def check_response(content) -> Dict:
        """
        Checks the response from the server.

        If the response contains an error message, it raises an appropriate exception.
        If the response is successful, it returns the data from the response.

        Parameters:
        response (Response): The response from the server.

        Returns:
        Dict: The data from the response if the request was successful.
        """
        if content.get("result") == "no credits":
            raise SmsAeroNoMoneyException(content["result"])
        if content.get("result") == "reject":
            raise SmsAeroException(content["reason"])
        if not content.get("success"):
            raise SmsAeroException(content.get("message") or "Unknown error")

        return content.get("data")

    def build_url(self, proto: str, selector: str, gate: str, page: Optional[int] = None) -> str:
        """
        Builds a URL for the request.

        Parameters:
        proto (str): The protocol for the URL (e.g., 'http' or 'https').
        selector (str): The selector for the URL.
        gate (str): The gateway for the URL.
        page (Optional[int], optional): The page number for the URL.

        Returns:
        str: The built URL.
        """
        url = urljoin(f"{proto}://{quote_plus(self.__user)}:{self.__akey}{gate}", selector)
        if page:
            url = urljoin(url, f"?page={int(page)}")
        return url

    async def request(
        self,
        selector: str,
        data: Optional[Dict] = None,
        page: Optional[int] = None,
        proto: str = "http",
    ) -> Dict:
        """
        Sends a request to the server.

        Parameters:
        selector (str): The selector for the URL.
        data (Dict[str, Any], optional): The data to be sent in the request. If not specified, no data will be sent.
        page (int, optional): The page number for the URL. If not specified, no page number will be added to the URL.
        proto (str, optional): The protocol for the URL (e.g., 'http' or 'https'). Default is 'https'.

        Returns:
        Dict: The data from the response if the request was successful.
        """
        await self.init_session()

        for gate in self.get_gate_urls():
            try:
                url = self.build_url(proto, selector, gate, page)
                if self.__sess is None:
                    raise SmsAeroConnectionException("Session is not initialized")
                async with self.__sess.post(url, json=data or {}, timeout=self.__time) as response:
                    logger.debug("Sending request to %s with data %s", url, data)
                    json = await response.json()
                    logger.debug("Received response: %s", json)
                    return self.check_response(json)
            except aiohttp.ClientSSLError:
                # switch to http when got ssl error
                proto = "http"
                continue
            except aiohttp.ClientError:
                # next gate
                continue
        raise SmsAeroConnectionException("All gateways are unavailable")


    async def send_sms(
        self,
        number: int,
        text: str,
        sign: Optional[str] = None,
        date_to_send: Optional[datetime.datetime] = None,
        callback_url: Optional[str] = None,
    ) -> Dict:
        """
        Sends a message to the specified number or numbers.

        Parameters:
        number (Union[int, List[int]]): The recipient's phone number or a list of phone numbers.
        text (str): The text of the message.
        sign (str, optional): The signature for the message.
        date_to_send (datetime, optional): The date and time when the message should be sent.
        callback_url (str, optional): The URL to which the server will send a request when the message status changes.

        Returns:
        Dict: The server's response in JSON format.

        Example response:
        {
            "id": 12345,
            "from": "Sms Aero",
            "number": "79031234567",
            "text": "Hello, World!",
            "status": 0,
            "extendStatus": "queue",
            "channel": "FREE SIGN",
            "cost": 5.49,
            "dateCreate": 1719119523,
            "dateSend": 1719119523
        }
        """
        data: Dict = {"text": text, "sign": sign or self.__sign, "callbackUrl": callback_url}
        data.update(**self.fill_nums(number))
        if date_to_send:
            data.update({"dateSend": int(time.mktime(date_to_send.timetuple()))})
        return await self.request("sms/send", data)