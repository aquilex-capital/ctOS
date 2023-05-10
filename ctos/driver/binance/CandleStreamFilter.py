from typing import Callable

from . import JSON


CandleStreamFilter = Callable[[JSON.Object], bool]


def closed_kline(kline: JSON.Object) -> bool:
    return kline["x"]
