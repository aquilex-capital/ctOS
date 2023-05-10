from __future__ import annotations
from typing import Iterator, Callable
from dataclasses import dataclass

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
    series commonly used by the `Predicate`s.
    """

    def __call__(self, candles: Candles) -> IndicativeCandles:
        """
        Each `Indicator` must override the `__call__` method. The resulting
        `IndicativeCandles` combine the original `Candles` columns with the
        columns provided by a concrete subclass of `Indicator`.

        NOTE: `Indicator`s must never mutate the original `Candles` instance.
        """
        raise NotImplementedError


class Indicators:
    """
    ## Overview

    The `Indicator`s are comparable and hashable on purpose. We want to be able
    to keep them in a `set` in order to prevent redundant recomputation.
    `Indicators` is a convenient wrapper to enable this.

    ## Examples

    ### Singleton Constructor

    ```
    batch = Indicators(SimpleMovingAverage("Value", 21))
    ```

    ### Composition

    #### Add one by one:

    ```
    batch = (
        batch
        << SimpleMovingAverage("Close", 89)
        << LinearRegressionChannel("Close", 2.0)
    )
    ```

    #### Union:

    ```
    batch = batch1 | batch2
    ```

    ### Length and Iteration

    ```
    i = 0
    for indicator in batch:
        i += 1
    assert i == len(batch)
    ```

    ### Use

    `Indicators` is itself (kind of) an indicator:

    ```
    indicative_candles = batch(candles)
    ```
    """

    def __init__(self, *indicators) -> None:
        self.indicators: set[Indicator] = set(indicators)

    def __lshift__(self, other: Indicator) -> Indicators:
        return Indicators(self.indicators.union([other]))

    def __or__(self, other: Indicators) -> Indicators:
        return Indicators(self.indicators.union(other.indicators))

    def __len__(self) -> int:
        return len(self.indicators)

    def __iter__(self) -> Iterator[Indicator]:
        for indicator in self.indicators:
            yield indicator

    def __call__(self, candles: Candles) -> IndicativeCandles:
        for indicator in self.indicators:
            candles = indicator(candles)
        return candles


@dataclass(unsafe_hash=True)
class SimpleMovingAverage(Indicator):
    column: str
    window: int
    name: str = "SMA"

    def __call__(self, candles: Candles) -> IndicativeCandles:
        sma = candles[self.column].rolling(window=self.window).mean()
        return candles.assign(**{self.name: sma})


@dataclass(unsafe_hash=True)
class ExponentialMovingAverage(Indicator):
    column: str
    window: int
    name: str = "EMA"

    def __call__(self, candles: Candles) -> IndicativeCandles:
        ema = candles[self.column].ewm(span=self.window, adjust=False).mean()
        return candles.assign(**{self.name: ema})


@dataclass(unsafe_hash=True)
class LinearRegressionChannel(Indicator):
    column: str
    deviation: float
    name: str = "LRC"

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
                f"{self.name}_U": upper_channel,
                f"{self.name}_M": y,
                f"{self.name}_L": lower_channel,
            }
        )