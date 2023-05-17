from __future__ import annotations
import logging as log
from typing import Callable, Optional
from datetime import datetime

from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient

from ctos.std.Candles import Candle, Candles
from ctos.func import always
from . import normalize
from .interval import Interval
from . import JSON


class BinanceFutures(UMFutures, UMFuturesWebsocketClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        proxy: str = "https://fapi.binance.com",
    ) -> None:
        UMFutures.__init__(self, key=api_key, secret=api_secret, base_url=proxy)
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

    def historical_candles(
        self,
        symbol: str,
        interval: Interval,
        start_time: datetime,
        end_time: datetime = datetime.now(),
        limit: int = 1500,  # ! This is also the maximum value
    ):
        return normalize.candles(
            self.klines(
                symbol=symbol,
                interval=str(interval),
                startTime=int(start_time.timestamp()) * 1000,
                endTime=int(end_time.timestamp()) * 1000,
                limit=limit,
            )
        )

    def stream_candles(
        self,
        symbol: str,
        interval: Interval,
        callback: Callable[[Candle], None],
        filter: Callable[[JSON.Object], bool] = always,
    ) -> None:
        def is_ok(event: JSON.Object) -> bool:
            event_type = "e"
            return event.get(event_type, None) == "kline"

        def middleware(event: JSON.Object) -> None:
            if is_ok(event) and filter(kline := event["k"]):
                callback(normalize.candle(kline))
            else:
                log.debug("skipping candle stream event: " + str(event))

        self.kline(
            id=0,
            symbol=symbol,
            interval=str(interval),
            callback=middleware,
        )

    def positions(self) -> JSON.ListOfObjects:
        return self.account()["positions"]

    def open_positions(self) -> JSON.ListOfObjects:
        return [
            position
            for position in self.positions()
            if float(position["positionAmt"]) != 0
        ]

    def position(self, symbol: str) -> float:
        try:
            match = filter(lambda p: p["symbol"] == symbol, self.positions())
            return float(next(match)["positionAmt"])
        except StopIteration:
            raise ValueError(f"Unknown symbol: {symbol}")

    def price_precision(self, symbol: str) -> int:
        return self.x_info[symbol]["pricePrecision"]

    def quantity_precision(self, symbol: str) -> int:
        return self.x_info[symbol]["quantityPrecision"]

    def position_size(self, symbol: str) -> float:
        """
        ```
        = 0 => Position doesn't exist
        < 0 => SELL position
        > 0 => BUY position
        ```
        """
        return float(
            next(
                filter(
                    lambda p: p["symbol"] == symbol,
                    self.positions(),
                )
            )["positionAmt"]
        )

    def all_symbols(self) -> list[str]:
        return [each["symbol"] for each in self.exchange_info()["symbols"]]
