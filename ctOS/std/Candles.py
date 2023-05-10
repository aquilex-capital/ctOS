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
