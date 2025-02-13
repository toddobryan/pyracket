from dataclasses import dataclass


class RkNumber:
    pass


class RkExact(RkNumber):
    pass


class RkExactReal(RkExact):
    pass


@dataclass
class RkInteger(RkExactReal):
    value: int


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
    digits: str
    exponent: int


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
