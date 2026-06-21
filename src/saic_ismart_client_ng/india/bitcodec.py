from __future__ import annotations

import math


class BitReader:
    def __init__(self, data: bytes | bytearray) -> None:
        self._data = data
        self._offset = 0

    @property
    def bit_offset(self) -> int:
        return self._offset

    def read_bits(self, bit_count: int) -> int:
        value = 0
        for _ in range(bit_count):
            byte_index = self._offset // 8
            bit_index = 7 - (self._offset % 8)
            value = (value << 1) | ((self._data[byte_index] >> bit_index) & 1)
            self._offset += 1
        return value

    def read_7bit_string(self, minimum: int, maximum: int) -> str:
        length = self.read_constrained_length(minimum, maximum)
        return "".join(chr(self.read_bits(7)) for _ in range(length))

    def read_constrained_length(self, minimum: int, maximum: int) -> int:
        span = maximum - minimum
        if span == 0:
            return minimum
        return minimum + self.read_bits(math.ceil(math.log2(span + 1)))


class BitWriter:
    def __init__(self) -> None:
        self._bits: list[int] = []

    def write_bits(self, value: int, bit_count: int) -> None:
        if value < 0 or value >= (1 << bit_count):
            msg = f"value does not fit in {bit_count} bits"
            raise ValueError(msg)
        for shift in range(bit_count - 1, -1, -1):
            self._bits.append((value >> shift) & 1)

    def write_7bit_string(self, value: str, minimum: int, maximum: int) -> None:
        if len(value) < minimum or len(value) > maximum:
            raise ValueError("string length outside constrained range")
        self.write_constrained_length(len(value), minimum, maximum)
        for char in value:
            code = ord(char)
            if code > 0x7F:
                raise ValueError("only 7-bit IA5 strings are supported")
            self.write_bits(code, 7)

    def write_constrained_length(self, value: int, minimum: int, maximum: int) -> None:
        if value < minimum or value > maximum:
            raise ValueError("length outside constrained range")
        span = maximum - minimum
        if span:
            self.write_bits(value - minimum, math.ceil(math.log2(span + 1)))

    def to_bytes(self) -> bytes:
        padding = (-len(self._bits)) % 8
        bits = [*self._bits, *([0] * padding)]
        output = bytearray()
        for offset in range(0, len(bits), 8):
            byte = 0
            for bit in bits[offset : offset + 8]:
                byte = (byte << 1) | bit
            output.append(byte)
        return bytes(output)


def read_fixed_7bit_string(data: bytes | bytearray, *, bit_offset: int, char_count: int) -> str:
    reader = BitReader(data)
    reader._offset = bit_offset  # noqa: SLF001
    return "".join(chr(reader.read_bits(7)) for _ in range(char_count))


def set_bits(data: bytearray, bit_offset: int, bit_count: int, value: int) -> None:
    if value < 0 or value >= (1 << bit_count):
        msg = f"value does not fit in {bit_count} bits"
        raise ValueError(msg)
    for index in range(bit_count):
        bit = (value >> (bit_count - index - 1)) & 1
        absolute = bit_offset + index
        byte_index = absolute // 8
        bit_index = 7 - (absolute % 8)
        if bit:
            data[byte_index] |= 1 << bit_index
        else:
            data[byte_index] &= ~(1 << bit_index)


def set_fixed_7bit_string(data: bytearray, bit_offset: int, value: str) -> None:
    for index, char in enumerate(value):
        code = ord(char)
        if code > 0x7F:
            raise ValueError("only 7-bit IA5 strings are supported")
        set_bits(data, bit_offset + index * 7, 7, code)
