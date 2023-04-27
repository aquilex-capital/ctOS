from __future__ import annotations
from typing import Callable

from ctOS.func import identity
from .Candles import Candles, IndicativeCandles
from .Indicator import IndicatorFunction, SimpleMovingAverage


PredicateFunction = Callable[[IndicativeCandles], bool]


class Predicate:
    """
    ```
    abstract class Predicate
    ```

    ## Overview

    Each `Predicate` can answer one simple question about the
    `IndicativeCandles` passed to it for evaluation.

    ## Logical Composition

    ```
    ~p       # invert
    p1 & p2  # logical AND
    p1 | p2  # logical OR
    ```
    """

    def __init__(
        self,
        predicate: PredicateFunction,
        indicator: IndicatorFunction = identity,
    ) -> None:
        self.indicator = indicator
        self.predicate = predicate

    def __call__(self, candles: Candles) -> bool:
        return self.predicate(self.indicator(candles))

    def __invert__(self) -> Predicate:
        return Predicate(lambda candles: not self(candles))

    def __and__(self, other: Predicate) -> Predicate:
        return Predicate(lambda candles: self(candles) and other(candles))

    def __or__(self, other: Predicate) -> Predicate:
        return Predicate(lambda candles: self(candles) or other(candles))


class LastClosePriceIsAboveSMA(Predicate):
    def __init__(self, window: int) -> None:
        column = "Close"
        self.SMA = f"SMA_{column}_{window}"
        super().__init__(self.predicate, SimpleMovingAverage(column, window))

    def predicate(self, candles: IndicativeCandles) -> bool:
        last_candle = candles.iloc[-1]
        return last_candle.Close > last_candle[self.SMA]
