from enum import Enum


class Interval(Enum):
    INTERVAL_1MINUTE = "1m"
    INTERVAL_3MINUTE = "3m"
    INTERVAL_5MINUTE = "5m"
    INTERVAL_15MINUTE = "15m"
    INTERVAL_30MINUTE = "30m"
    INTERVAL_1HOUR = "1h"
    INTERVAL_2HOUR = "2h"
    INTERVAL_4HOUR = "4h"
    INTERVAL_6HOUR = "6h"
    INTERVAL_8HOUR = "8h"
    INTERVAL_12HOUR = "12h"
    INTERVAL_1DAY = "1d"
    INTERVAL_3DAY = "3d"
    INTERVAL_1WEEK = "1w"
    INTERVAL_1MONTH = "1M"

    def __str__(self) -> str:
        return self.value
