from dataclasses import dataclass
from enum import Enum

class Base(Enum):
    BINARY = 2
    OCTAL = 8
    DECIMAL = 10
    HEXADECIMAL = 16


BASE_TO_ALPH = {
    Base.BINARY: "01",
    Base.OCTAL: "01234567",
    Base.DECIMAL: "0123456789",
    Base.HEXADECIMAL : "0123456789abcdefABCDEF",
}


class RkNumber:
    pass


class RkExact(RkNumber):
    pass


class RkExactReal(RkExact):
    pass


@dataclass
class RkInteger(RkExactReal):
    value: int

@dataclass
class RkRational(RkExactReal):
    # normalized so that denominator is always positive
    numerator: int
    denominator: int

    def __init__(self, num: int, denom: int) -> None:
        if denom == 0:
            raise ValueError("denominator cannot be zero")
        elif denom < 0:
            num, denom = -num, -denom
        self.numerator = num
        self.denominator = denom


@dataclass
class RkExactFloatingPoint(RkExactReal):
    base: Base
    digits: str
    exponent: str


@dataclass
class RkExactComplex(RkExact):
    real: RkExactReal
    imaginary: RkExactReal


class RkInexact(RkNumber):
    pass


class RkInexactReal(RkInexact):
    value: float


class RkInexactComplex(RkInexact):
    real: float
    imaginary: float
