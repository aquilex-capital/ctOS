from typing import Any
from datetime import datetime

import pandas as pd

from ctOS.std.Candles import Candle, Candles


def candles(klines: list[dict[str, Any]]) -> Candles:
    """
    [
        {
            1591258320000,  # Open time
            "9640.7",       # Open
            "9642.4",       # High
            "9640.6",       # Low
            "9642.0",       # Close (or latest price)
            "206",          # Volume
            1591258379999,  # Close time
            "2.13660389",   # Base asset volume
            48,             # Number of trades
            "119",          # Taker buy volume
            "1.23424865",   # Taker buy base asset volume
            "0"             # Ignore.
        }
    ]
    """

    df = pd.DataFrame(
        data=klines,
        columns=[
            "OpenTime",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
            "CloseTime",
            "Base asset volume",
            "Number of trades",
            "Taker by volume",
            "Taker buy base asset volume",
            "Unused",
        ],
    )
    df.OpenTime = (df.OpenTime // 1000).apply(datetime.fromtimestamp)
    df.CloseTime = (df.CloseTime // 1000).apply(datetime.fromtimestamp)
    df.Volume = pd.to_numeric(df["Volume"], errors="raise")
    df.Open = pd.to_numeric(df["Open"], errors="raise")
    df.High = pd.to_numeric(df["High"], errors="raise")
    df.Low = pd.to_numeric(df["Low"], errors="raise")
    df.Close = pd.to_numeric(df["Close"], errors="raise")
    df.set_index(df.CloseTime, inplace=True)
    df.drop(
        columns=[
            "CloseTime",
            "Base asset volume",
            "Number of trades",
            "Taker by volume",
            "Taker buy base asset volume",
            "Unused",
        ],
        inplace=True,
    )
    return df


def candle(kline: dict[str, Any]) -> Candle:
    """
    {
        "t":1591261500000,  # Kline start time
        "T":1591261559999,  # Kline close time
        "i":"1m",           # Interval
        "f":606400,         # First trade ID
        "L":606430,         # Last trade ID
        "o":"9638.9",       # Open price
        "c":"9639.8",       # Close price
        "h":"9639.8",       # High price
        "l":"9638.6",       # Low price
        "v":"156",          # volume
        "n":31,             # Number of trades
        "x":false,          # Is this kline closed?
        "q":"1.61836886",   # Base asset volume
        "V":"73",           # Taker buy volume
        "Q":"0.75731156",   # Taker buy base asset volume
        "B":"0"             # Ignore
    }
    """

    df = pd.DataFrame(
        data={
            "OpenTime": [kline["t"]],
            "CloseTime": [kline["T"]],
            "Volume": [kline["v"]],
            "Open": [kline["o"]],
            "High": [kline["h"]],
            "Low": [kline["l"]],
            "Close": [kline["c"]],
        }
    )
    df.OpenTime = (df.OpenTime // 1000).apply(datetime.fromtimestamp)
    df.CloseTime = (df.CloseTime // 1000).apply(datetime.fromtimestamp)
    df.Volume = pd.to_numeric(df.Volume, errors="raise")
    df.Open = pd.to_numeric(df.Open, errors="raise")
    df.High = pd.to_numeric(df.High, errors="raise")
    df.Low = pd.to_numeric(df.Low, errors="raise")
    df.Close = pd.to_numeric(df.Close, errors="raise")
    df.set_index(df.CloseTime, inplace=True)
    df.drop(columns=["CloseTime"], inplace=True)
    return df
