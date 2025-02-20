from dataclasses import dataclass
from decimal import Decimal
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
    base: Base
    value: int

@dataclass
class RkRational(RkExactReal):
    base: Base
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

class RkExactFloatingPoint(RkExactReal):
    base: Base
    digits: str
    exponent: str
    dec: Decimal

    def __init__(self, base: Base, digits: str, exponent: str) -> None:
        self.base = base
        self.digits = digits
        self.exponent = exponent
        self.dec = (int(digits, base.value)
                    * base.value ** int(exponent, base.value))

    def __str__(self) -> str:
        return str(self.dec)


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
