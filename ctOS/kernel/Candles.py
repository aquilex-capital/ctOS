import pandas as pd


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
