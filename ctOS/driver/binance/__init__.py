from __future__ import annotations
import logging as log
from typing import Callable, Optional

from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

from ctOS.std.Candles import Candle, Candles
from ctOS.func import always
from . import normalize
from .interval import Interval
from .CandleStreamFilter import CandleStreamFilter
from . import JSON


class BinanceFutures(UMFutures, UMFuturesWebsocketClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ) -> None:
        UMFutures.__init__(self, key=api_key, secret=api_secret)
        UMFuturesWebsocketClient.__init__(self)
        self.x_info = dict(
            [(symbol["symbol"], symbol) for symbol in self.exchange_info()["symbols"]]
        )

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
        filter: CandleStreamFilter = always,
    ) -> None:
        def is_ok(event: JSON.Object) -> bool:
            event_type = "e"
            return event.get(event_type, None) == "kline"

        def middleware(event: JSON.Object) -> None:
            if is_ok(event) and filter(kline := event["k"]):
                callback(normalize.candle(kline))
            else:
                log.warning("skipping candle stream event: " + str(event))

        self.kline(
            id=0,
            symbol=symbol,
            interval=str(interval),
            callback=middleware,
        )

    def open_positions(
        self, symbol: str = None
    ) -> tuple[JSON.ObjectList, Optional[JSON.Object]]:
        all_open = [
            position
            for position in self.account()["positions"]
            if float(position["positionAmt"]) != 0
        ]
        open_for_symbol = [
            position for position in all_open if position["symbol"] == symbol
        ]
        return all_open, open_for_symbol[0] if open_for_symbol else None

    def price_precision(self, symbol: str) -> int:
        return self.x_info[symbol]["pricePrecision"]

    def quantity_precision(self, symbol: str) -> int:
        return self.x_info[symbol]["quantityPrecision"]
