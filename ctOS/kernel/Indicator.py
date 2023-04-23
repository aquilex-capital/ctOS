from __future__ import annotations
from typing import Callable, Iterator, Iterable
from dataclasses import dataclass
import traceback

import numpy as np

from .Candles import Candles, IndicativeCandles


IndicatorFunction = Callable[[Candles], IndicativeCandles]


@dataclass(unsafe_hash=True)
class Indicator:
    """
    ```
    abstract class Indicator
    ```

    ## Overview

    `Indicator`s provide additional quantitative information about the `Candles`
    series commonly used by the `Signal`s.

    ## Functional Composition

    ```
    indicator1 >> indicator2  # 1 then 2
    indicator1 << indicator2  # 2 then 1
    ```
    """

    def __call__(self, candles: Candles) -> IndicativeCandles:
        """
        Each `Indicator` must override the `__call__` method. The resulting
        `IndicativeCandles` combine the original `Candles` columns with the
        columns provided by a concrete subclass of `Indicator`.

        NOTE 1: this method follows the signature of the `IndicatorFunction`.

        NOTE 2: `Indicator`s must never mutate the original `Candles` instance.
        """
        raise NotImplementedError


class IndicatorBatch:
    @staticmethod
    def singleton(indicator: Indicator) -> IndicatorBatch:
        return IndicatorBatch([indicator])

    def __init__(self, indicators: Iterable[Indicator]) -> None:
        self.indicators = set(indicators)

    def __len__(self) -> int:
        return len(self.indicators)

    def __iter__(self) -> Iterator[Indicator]:
        for indicator in self.indicators:
            yield indicator

    def __lshift__(self, other: Indicator) -> IndicatorBatch:
        return IndicatorBatch(self.indicators.union([other]))

    def __or__(self, other: IndicatorBatch) -> IndicatorBatch:
        return IndicatorBatch(self.indicators.union(other.indicators))

    def __call__(self, candles: Candles) -> IndicativeCandles:
        for indicator in self.indicators:
            candles = indicator(candles)
        return candles


@dataclass(eq=False)
class SimpleMovingAverage(Indicator):
    column: str
    window: int

    def __call__(self, candles: Candles) -> IndicativeCandles:
        sma = candles[self.column].rolling(window=self.window).mean()
        return candles.assign(**{f"SMA_{self.column}_{self.window}": sma})


@dataclass(eq=False)
class ExponentialMovingAverage(Indicator):
    column: str
    window: int

    def __call__(self, candles: Candles) -> IndicativeCandles:
        ema = candles[self.column].ewm(span=self.window, adjust=False).mean()
        return candles.assign(**{f"EMA_{self.column}_{self.window}": ema})


@dataclass(eq=False)
class LinearRegressionChannel(Indicator):
    column: str
    deviation: float

    def __call__(self, candles: Candles) -> IndicativeCandles:
        series = candles[self.column]

        # Calculate the linear regression line
        x = np.arange(len(series))
        slope, intercept = np.polyfit(x, series, 1)
        y = slope * x + intercept

        # Calculate the standard deviation of the residuals
        residuals = series - y
        std_dev = np.std(residuals)

        upper_channel = y + std_dev * self.deviation
        lower_channel = y - std_dev * self.deviation

        return candles.assign(
            **{
                f"LRC_{self.column}_U": upper_channel,
                f"LRC_{self.column}_M": y,
                f"LRC_{self.column}_L": lower_channel,
            }
        )
