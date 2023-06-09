from __future__ import annotations
import logging as log
from typing import Callable, Optional
from datetime import datetime

from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
import pandas as pd

from ctos.std.Candles import Candle, Candles
from ctos.func import always
from . import normalize
from .Interval import Interval
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
        self._info = dict(
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

    def history(
        self,
        symbol: str,
        interval: Interval,
        start_time: datetime,
        end_time: Optional[datetime] = None,
    ) -> Candles:
        end_time = datetime.now() if end_time is None else end_time

        def starting_at(start: datetime) -> Candles:
            return self._fetch_chunk(symbol, interval, start, end_time)

        data = starting_at(start_time)
        while (last_end := data.index[-1].to_pydatetime()) < end_time:  # type: ignore
            data = pd.concat([data, starting_at(start=last_end)])

        return data[:end_time]

    def _fetch_chunk(
        self,
        symbol: str,
        interval: Interval,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1500,  # ! This is also the maximum value
    ) -> Candles:
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
            symbol=symbol,
            interval=str(interval),
            callback=middleware,
            id=0,
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
        return self._info[symbol]["pricePrecision"]

    def quantity_precision(self, symbol: str) -> int:
        return self._info[symbol]["quantityPrecision"]

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
        return [each["symbol"] for each in self._info["symbols"]]
