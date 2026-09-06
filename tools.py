from typing import Iterable


def splitWord(w: int) -> tuple[int, int]:
    a = w & 0xFF
    b = w >> 8
    return a, b


def splitThree(t: int) -> tuple[int, int, int]:
    a = t & 0xFF
    b = (t >> 8) & 0xFF
    c = t >> 16
    return a, b, c


def splitString(s: str) -> Iterable[int]:
    chars = [ord(c) for c in s]
    chars.append(0xFF)
    return chars


def hexBytes(by: bytes, fmt: str = "%02x") -> str:
    s = "$"
    for b in by:
        s += fmt % b
    return s


def asNumber(raw: str) -> int:
    if raw.startswith("0x"):
        return int(raw, 16)
    return int(raw)
