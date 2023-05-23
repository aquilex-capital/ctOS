from __future__ import annotations
from typing import Iterator, Callable
from dataclasses import dataclass

import numpy as np

from ctos.std.Candles import Candles, IndicativeCandles

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


@dataclass(unsafe_hash=True)
class BollingerBands(Indicator):
    column: str
    window: int
    deviation: float
    name: str = "BOLL"

    def __call__(self, candles: Candles) -> IndicativeCandles:
        rolling = candles[self.column].rolling(self.window)
        mean = rolling.mean()
        std = rolling.std() * self.deviation
        upper_band = mean + std
        lower_band = mean - std
        return candles.assign(
            **{
                f"{self.name}_U": upper_band,
                f"{self.name}_M": mean,
                f"{self.name}_L": lower_band,
            }
        )


@dataclass(unsafe_hash=True)
class TrueStrengthIndex(Indicator):
    column: str
    long_window: int
    short_window: int
    name: str = "TSI"

    def __call__(self, candles: Candles) -> IndicativeCandles:
        price_change = candles[self.column].diff()
        abs_price_change = price_change.abs()

        price_change_double_smoothed = (
            price_change.ewm(span=self.long_window, adjust=False)
            .mean()
            .ewm(span=self.short_window, adjust=False)
            .mean()
        )
        abs_price_change_double_smoothed = (
            abs_price_change.ewm(span=self.long_window, adjust=False)
            .mean()
            .ewm(span=self.short_window, adjust=False)
            .mean()
        )

        tsi = price_change_double_smoothed / abs_price_change_double_smoothed
        return candles.assign(**{self.name: tsi})


@dataclass(unsafe_hash=True)
class PriceVolumeRatio(Indicator):
    name: str = "PVR"

    def __call__(self, candles: Candles) -> IndicativeCandles:
        pvr = (candles.Close - candles.Open) / candles.Volume
        return candles.assign(**{self.name: pvr})


@dataclass(unsafe_hash=True)
class AbsolutePriceVolumeRatio(Indicator):
    PVR = PriceVolumeRatio()

    name: str = "APVR"

    def __call__(self, candles: Candles) -> IndicativeCandles:
        apvr = self.PVR(candles).PVR.abs()
        return candles.assign(**{self.name: apvr})


@dataclass(unsafe_hash=True)
class MeanAverageConvergenceDivergence(Indicator):
    column: str
    short_window: int
    long_window: int
    signal_window: int
    name: str = "MACD"

    def __call__(self, candles: Candles) -> IndicativeCandles:
        short_ema = (
            candles[self.column].ewm(span=self.short_window, adjust=False).mean()
        )
        long_ema = candles[self.column].ewm(span=self.long_window, adjust=False).mean()
        macd_line = short_ema - long_ema
        signal_line = macd_line.ewm(span=self.signal_window, adjust=False).mean()
        macd_histogram = macd_line - signal_line
        return candles.assign(
            **{
                self.name: macd_line,
                f"{self.name}_SIGNAL": signal_line,
                f"{self.name}_HIST": macd_histogram,
            }
        )


@dataclass(unsafe_hash=True)
class RelativeStrengthIndex(Indicator):
    column: str
    window: int
    name: str = "RSI"

    def __call__(self, candles: Candles) -> IndicativeCandles:
        price_diff = candles[self.column].diff()

        gain = price_diff.where(price_diff > 0, 0)
        loss = -price_diff.where(price_diff < 0, 0)

        avg_gain = gain.rolling(window=self.window).mean()
        avg_loss = loss.rolling(window=self.window).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - 100 / (1 + rs)

        return candles.assign(**{self.name: rsi})


@dataclass(unsafe_hash=True)
class RateOfChange(Indicator):
    column: str
    window: int
    name: str = "ROC"

    def __call__(self, candles: Candles) -> IndicativeCandles:
        roc = (
            (candles[self.column] - candles[self.column].shift(self.window))
            / candles[self.column].shift(self.window)
            * 100
        )
        return candles.assign(**{self.name: roc})


@dataclass(unsafe_hash=True)
class AngularMomentumRatio(Indicator):
    column: str
    short_window: int
    long_window: int
    name: str = "AMR"

    def __call__(self, candles: Candles) -> IndicativeCandles:
        short_dy = (
            candles[self.column].ewm(span=self.short_window, adjust=False).mean().diff()
        )
        long_dy = (
            candles[self.column].ewm(span=self.long_window, adjust=False).mean().diff()
        )
        amr = short_dy / long_dy
        return candles.assign(**{self.name: amr})
