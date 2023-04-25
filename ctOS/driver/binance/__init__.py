from __future__ import annotations
import logging as log
from enum import Enum
from typing import Any, Callable, Optional

from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

from ctOS.std.Candles import Candle, Candles
from . import normalize


class Interval(Enum):
    INTERVAL_1MINUTE = "1m"
    INTERVAL_3MINUTE = "3m"
    INTERVAL_5MINUTE = "5m"
    INTERVAL_15MINUTE = "15m"
    INTERVAL_30MINUTE = "30m"
    INTERVAL_1HOUR = "1h"
    INTERVAL_2HOUR = "2h"
    INTERVAL_4HOUR = "4h"
    INTERVAL_6HOUR = "6h"
    INTERVAL_8HOUR = "8h"
    INTERVAL_12HOUR = "12h"
    INTERVAL_1DAY = "1d"
    INTERVAL_3DAY = "3d"
    INTERVAL_1WEEK = "1w"
    INTERVAL_1MONTH = "1M"

    def __str__(self) -> str:
        return self.value


class BinanceFutures(UMFutures, UMFuturesWebsocketClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ) -> None:
        UMFutures.__init__(self, key=api_key, secret=api_secret)
        UMFuturesWebsocketClient.__init__(self)

    def candles(
        self,
        symbol: str,
        interval: Interval,
        limit: int,
    ) -> Candles:
        return normalize.candles(
            self.klines(
                symbol=symbol,
                interval=str(interval),
                limit=limit,
            )
        )

    def stream_candles(
        self,
        symbol: str,
        interval: Interval,
        callback: Callable[[Candle], None],
        filter: Callable[[Candle], bool] = lambda _: True,
    ) -> None:
        def is_ok(event: dict[str, Any]) -> bool:
            event_type = "e"
            return event.get(event_type, None) == "kline"

        def middleware(event: dict[str, Any]) -> None:
            if is_ok(event) and filter(candle := normalize.candle(event["k"])):
                callback(candle)
            else:
                log.warning("skipping candle stream event: " + str(event))

        self.kline(
            id=0,
            symbol=symbol,
            interval=str(interval),
            callback=middleware,
        )
