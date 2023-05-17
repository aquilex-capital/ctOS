from . import JSON


def closed_kline(kline: JSON.Object) -> bool:
    return kline["x"]
