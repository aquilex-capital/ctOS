from dataclasses import dataclass

import pandas as pd


Candle = pd.DataFrame
"""Represents one row of Candles."""


Candles = pd.DataFrame
"""
Represents a series of candle bars.

```
type alias Candles = 
    { OpenTime  : list[datetime]
    , CloseTime : list[datetime]  # index
    , Volume    : list[int]
    , Open      : list[float]
    , High      : list[float]
    , Low       : list[float]
    , Close     : list[float]
    }
```
"""

IndicativeCandles = pd.DataFrame
"""
`Indicator`s produce `IndicativeCandles` - the composition of the original
`Candles` with some additional columns.
"""


@dataclass
class CandleCache:
    candles: Candles

    def push(self, candle: Candle) -> None:
        self.candles = pd.concat([self.candles, candle]).iloc[1:]

    def view(self) -> Candles:
        return self.candles.copy(deep=False)


def candles_from_csv(path: str) -> Candles:
    data = pd.read_csv(path)
    data.CloseTime = pd.to_datetime(data.CloseTime)
    data.OpenTime = pd.to_datetime(data.OpenTime)
    data.set_index("CloseTime", inplace=True)
    return data
