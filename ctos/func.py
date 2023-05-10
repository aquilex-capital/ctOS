"""Functional primitives."""

from typing import Any


def identity(x: Any) -> Any:
    return x


def always(_: Any) -> bool:
    return True


def never(_: Any) -> bool:
    return False
