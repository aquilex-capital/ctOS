from typing import Callable
import logging as log
from dataclasses import dataclass

from requests import Response, post


@dataclass
class Notifier:
    bot_token: str
    chat_id: int

    def highjack_arguments(self, function: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            text = " ".join(map(str, list(args) + list(kwargs.values())))
            if (resp := self.notify(text)) and resp.status_code != 200:
                log.error(resp)
            return function(*args, **kwargs)

        return wrapper

    def highjack_return_value(self, function: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            result = function(*args, **kwargs)
            if (resp := self.notify(str(result))) and resp.status_code != 200:
                log.error(resp)
            return result

        return wrapper

    def notify(self, text: str) -> Response:
        log.info(text)
        return post(
            url=f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
            json={
                "chat_id": self.chat_id,
                "text": text,
            },
        )
