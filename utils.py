def decimal_to_binary(decimal: int, length: int) -> str: 
    if decimal < 0:  # check if the number is negative
        raise ValueError("decimal must be ≥ 0")  # raise error for negative numbers
    binary = bin(decimal)[2:]  # convert to binary and remove the '0b' prefix
    if len(binary) > length:  # check if it fits in the specified number of bits
        raise ValueError("does not fit in length bits")  # raise error if it doesn't fit
    while len(binary) < length:  # pad with zeros on the left
        binary = "0" + binary  # until reaching the correct length
    return binary  # return the padded binary string

def decimal_to_binary_signed(decimal: int, length: int) -> str:  
    if decimal >= 0:  # check if the number is positive
        return decimal_to_binary(decimal, length)  # use unsigned conversion
    positive = abs(decimal)  # get the absolute value
    binary = bin(positive)[2:]  # convert to binary without sign
    if len(binary) > length:  # check if it fits
        raise ValueError("does not fit in length bits")  # raise error if not
    while len(binary) < length:  # pad with zeros on the left
        binary = "0" + binary  # until reaching the correct length
    inverted = ""  # initialize for bit inversion
    for b in binary:  # invert each bit
        inverted += "1" if b == "0" else "0" 
    total = int(inverted, 2) + 1  # add one to get two's complement
    result = bin(total)[2:]  # convert result to binary
    while len(result) < length:  # pad if necessary
        result = "0" + result  # add zeros
    if len(result) > length:  # check if it overflows
        raise ValueError("negative does not fit in length bits")  # raise error if overflow
    return result  # return the two's complement binary string

def binary_to_decimal(bin_string: str) -> int:  
    for c in bin_string:  # check each character
        if c not in ("0", "1"):  # only allow valid binary digits
            raise ValueError("non-binary string")  # raise error if not binary
    return int(bin_string, 2)  # return the integer value

def binary_to_decimal_signed(bin_string: str) -> int:  
    if not bin_string:  # if the input is empty
        raise ValueError("invalid binary input")  # raise format error
    for c in bin_string:  # check each character
        if c not in ("0", "1"):  # only allow binary digits
            raise ValueError("invalid binary input")  # raise format error
    if bin_string[0] == "0":  # if the first bit is 0, it's positive
        return int(bin_string, 2)  # return directly
    inverted = ""  # initialize for inversion
    for b in bin_string:  # invert each bit
        inverted += "1" if b == "0" else "0" 
    value = int(inverted, 2) + 1  # add one to get two's complement
    return -value  # return the negative value

