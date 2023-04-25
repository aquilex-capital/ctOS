from typing import Iterable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"

    def __str__(self) -> str:
        return self.value


@dataclass
class Signal:
    side: Side
    symbol: str
    price: float
    at: datetime

    def __str__(self) -> str:
        return f"{self.side} {self.symbol} at {self.at} for {self.price} USDT"
