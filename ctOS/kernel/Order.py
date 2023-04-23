from typing import Iterable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class Action(Enum):
    BUY = "BUY"
    SELL = "SELL"

    def __str__(self) -> str:
        return "BUY" if self == Action.BUY else "SELL"

    def __repr__(self) -> str:
        return str(self)


@dataclass
class Order:
    action: Action
    symbol: str
    price: float
    at: datetime

    def __str__(self) -> str:
        return f"{self.action} {self.symbol} at {self.at} for {self.price} USDT"

    def __repr__(self) -> str:
        return str(self)


OrderBatch = Iterable[Order]
