from __future__ import annotations
from typing import Callable, Iterable

from .Candles import Candles, IndicativeCandles
from .Indicator import Indicator, IndicatorBatch, SimpleMovingAverage


SignalFunction = Callable[[IndicativeCandles], bool]


class Signal:
    """
    ```
    abstract class Signal
    ```

    ## Overview

    Each `Signal` can answer one simple question about the `IndicativeCandles`
    passed to it for evaluation.

    ## Logical Composition

    ```
    ~signal            # invert
    signal1 & signal2  # logical AND
    signal1 | signal2  # logical OR
    ```
    """

    def __init__(self, indicators: Iterable[Indicator], signal: SignalFunction) -> None:
        self.indicators = IndicatorBatch(indicators)
        self.signal = signal

    def __call__(self, candles: Candles) -> bool:
        return self.signal(self.indicators(candles))

    def __invert__(self) -> Signal:
        return Signal(self.indicators, lambda candles: not self.signal(candles))

    def __and__(self, other: Signal) -> Signal:
        return Signal(
            self.indicators | other.indicators,
            lambda candles: self.signal(candles) and other.signal(candles),
        )

    def __or__(self, other: Signal) -> Signal:
        return Signal(
            self.indicators | other.indicators,
            lambda candles: self.signal(candles) or other.signal(candles),
        )


class LastClosePriceIsAboveSMA(Signal):
    def __init__(self, window: int) -> None:
        column = "Close"
        self.SMA = f"SMA_{column}_{window}"
        super().__init__(
            indicators=[SimpleMovingAverage(column, window)],
            signal=self.signal,
        )

    def signal(self, candles: IndicativeCandles) -> bool:
        last_candle = candles.iloc[-1]
        return last_candle.Close > last_candle[self.SMA]
