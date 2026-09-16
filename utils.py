def decimal_to_unsigned_bin(value: int, bits: int) -> str:
    if value < 0:
        raise ValueError(f"Value {value} is negative")
    if value >= (1 << bits):
        raise ValueError(f"Value {value} does not fit in {bits} bits")
    return format(value, f"0{bits}b")


def decimal_to_signed_bin(value: int, bits: int) -> str:
    if value >= 0:
        return decimal_to_unsigned_bin(value, bits)
    mask = (1 << bits) - 1
    return format(value & mask, f"0{bits}b")


def unsigned_bin_to_decimal(bin_str: str) -> int:
    for c in bin_str:
        if c not in ("0", "1"):
            raise ValueError(f"Invalid binary character: {c}")
    return int(bin_str, 2)


def signed_bin_to_decimal(bin_str: str) -> int:
    if not bin_str:
        raise ValueError("Empty binary string")
    for c in bin_str:
        if c not in ("0", "1"):
            raise ValueError(f"Invalid binary character: {c}")
    value = int(bin_str, 2)
    if bin_str[0] == "1":
        value -= (1 << len(bin_str))
    return value
