from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class PosOrNeg(Enum):
    POS = "+"
    NEG = "-"


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

    def __init__(self, base: Base, num: int, denom: int) -> None:
        if denom == 0:
            raise ValueError("denominator cannot be zero")
        elif denom < 0:
            num, denom = -num, -denom
        self.base = base
        self.numerator = num
        self.denominator = denom

class RkExactFloatingPoint(RkExactReal):
    base: Base
    digits: str
    exponent: RkInteger
    dec: Decimal

    def __init__(
            self,
            base: Base,
            sign: PosOrNeg,
            digits: str,
            exponent: RkInteger
    ) -> None:
        self.base = base
        self.sign = sign
        self.digits = digits
        self.exponent = exponent
        self.dec = ((-1 if sign is PosOrNeg.NEG else 1)
                    * Decimal(int(digits, base.value))
                    * Decimal(base.value) ** exponent.value)

    def __eq__(self, other):
        if isinstance(other, RkExactFloatingPoint):
            # ignore dec, since it is derived from the other fields
            return (self.base == other.base
                    and self.sign == other.sign
                    and self.digits == other.digits
                    and self.exponent == other.exponent)

    def __str__(self) -> str:
        return str(self.dec)

    def __repr__(self) -> str:
        return (f"RkExactFloatingPoint({self.base}, "
                + f"{self.sign}, {self.digits}, {self.exponent})")


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
