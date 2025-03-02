import decimal
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Optional


class PosOrNeg(Enum):
    POS = "+"
    NEG = "-"

    def negate(self) -> "PosOrNeg":
        if self == PosOrNeg.NEG:
            return PosOrNeg.POS
        else:
            return PosOrNeg.NEG


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
    def negate(self):
        pass


class RkExact(RkNumber):
    pass


class RkExactReal(RkExact):
    pass


@dataclass
class RkInteger(RkExactReal):
    base: Base
    value: int

    def negate(self):
        return RkInteger(self.base, -1 * self.value)

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

    def negate(self):
        return RkRational(self.base, -1 * self.numerator, self.denominator)

@dataclass
class RkExactFloatingPoint(RkExactReal):
    base: Base
    sign: PosOrNeg
    digits: str
    exponent: RkInteger
    _dec: Optional[Decimal] = (
        field(init=False, repr=False, compare=False, default=None))

    def dec(self) -> Decimal:
        if not self._dec:
            new_prec = max(len(self.digits), decimal.getcontext().prec)
            decimal.setcontext(decimal.Context(prec=new_prec))
            self._dec = ((-1 if self.sign is PosOrNeg.NEG else 1)
                    * Decimal(int(self.digits, self.base.value))
                     * Decimal(self.base.value) ** Decimal(self.exponent.value))
        return self._dec

    def negate(self) -> "RkExactFloatingPoint":
        return RkExactFloatingPoint(
            self.base, self.sign.negate(), self.digits, self.exponent)


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
