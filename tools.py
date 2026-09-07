from strings import encode


def split_word(w: int):
    a = w & 0xFF
    b = w >> 8
    return a, b


def split_three(t: int):
    a = t & 0xFF
    b = (t >> 8) & 0xFF
    c = t >> 16
    return a, b, c


def split_string(s: str):
    chars = list(encode(s))
    chars.append(0xFF)
    return chars


def hex_bytes(by: bytes, fmt: str = "%02x"):
    s = "$"
    for b in by:
        s += fmt % b
    return s


def as_number(raw: str):
    if raw.lower().startswith("0x"):
        return int(raw, 16)
    return int(raw)
