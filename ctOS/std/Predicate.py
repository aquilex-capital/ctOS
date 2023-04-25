from __future__ import annotations
from typing import Callable, Iterable

from .Candles import Candles, IndicativeCandles
from .Indicator import Indicator, IndicatorBatch, SimpleMovingAverage


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
        indicators: Iterable[Indicator],
        predicate: PredicateFunction,
    ) -> None:
        self.indicators = IndicatorBatch(indicators)
        self.predicate = predicate

    def __call__(self, candles: Candles) -> bool:
        return self.predicate(self.indicators(candles))

    def __invert__(self) -> Predicate:
        return Predicate(self.indicators, lambda candles: not self.predicate(candles))

    def __and__(self, other: Predicate) -> Predicate:
        return Predicate(
            self.indicators | other.indicators,
            lambda candles: self.predicate(candles) and other.predicate(candles),
        )

    def __or__(self, other: Predicate) -> Predicate:
        return Predicate(
            self.indicators | other.indicators,
            lambda candles: self.predicate(candles) or other.predicate(candles),
        )


class LastClosePriceIsAboveSMA(Predicate):
    def __init__(self, window: int) -> None:
        column = "Close"
        self.SMA = f"SMA_{column}_{window}"
        super().__init__(
            indicators=[SimpleMovingAverage(column, window)],
            predicate=self.predicate,
        )

    def predicate(self, candles: IndicativeCandles) -> bool:
        last_candle = candles.iloc[-1]
        return last_candle.Close > last_candle[self.SMA]
