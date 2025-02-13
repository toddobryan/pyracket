from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Optional, Union

from lark import Transformer, v_args
from lark.tree import Meta

from ..semantics.numbers import RkNumber, RkExact, RkExactReal, RkInteger, \
    RkRational, RkExactFloatingPoint
from .expr_ast import PyracketAst

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

class PosOrNeg(Enum):
    POS = "+"
    NEG = "-"

    @staticmethod
    def of[B](x: "Int") -> "PosOrNeg":
        return PosOrNeg.POS if x.value >= 0 else PosOrNeg.NEG

T = TypeVar("T")
B = TypeVar("B", bound=Base)
N = TypeVar("N", bound=RkNumber)
E = TypeVar("E", bound=RkExact)
R = TypeVar("R", bound=RkExactReal)

class NumberAst[N](PyracketAst[N]):
    value: N


class ExactAst[E](NumberAst[E]):
    pass


class ExactRealAst[R](ExactAst[R]):
    base: B

@dataclass
class IntegerAst[B](ExactRealAst[RkInteger]):
    meta: Meta
    base: B
    value: RkInteger

@dataclass
class RationalAst[B](ExactAst[RkRational]):
    meta: Meta
    base: B
    value: RkRational

@dataclass
class ExactFloatingPointAst[B](ExactRealAst[RkExactFloatingPoint]):
    meta: Meta
    base: B
    pos_or_neg: PosOrNeg
    digits: str
    exponent: int





    @staticmethod
    def make[B](base: B, numerator: Int[B], denominator: Int[B]) -> "Rational":
        pos_or_neg = PosOrNeg.POS \
            if PosOrNeg.of(numerator) == PosOrNeg.of(denominator) \
            else PosOrNeg.NEG
        return Rational(base, pos_or_neg, numerator, denominator)

@dataclass
class Complex(NumberAst):
    real: Rational
    imaginary: Rational


@dataclass
class ComplexExact(NumberAst):
    meta: Meta
    value: Complex

@dataclass
class RationalExact(NumberAst):
    meta: Meta
    value: "Number"

@dataclass
class UnsignedRational[B](NumberAst):
    meta: Meta
    base: B
    num: Int[B]
    denom: Int[B]

@dataclass
class Sign(PyracketAst):
    meta: Meta
    value: PosOrNeg

    def __init__(self, meta: Meta, value: Optional[str]) -> None:
        self.meta = meta
        self.value = PosOrNeg.POS if value is None else PosOrNeg(value)

class ToAstExact(Transformer):
    @v_args(inline=True, meta=True)
    def UNSIGNED_INTEGER_2(self, meta, s) -> Int:
        return Int(meta, 2, int(s, 2))

    @v_args(inline=True, meta=True)
    def UNSIGNED_INTEGER_8(self, meta, s) -> Int:
        return Int(meta, 8, int(s, 8))

    @v_args(inline=True, meta=True)
    def UNSIGNED_INTEGER_10(self, meta, s) -> Int:
        return Int(meta, 10, int(s))

    @v_args(inline=True, meta=True)
    def UNSIGNED_INTEGER_16(self, meta, s) -> Int:
        return Int(meta, 16, int(s, 16))

    def OPT_DECIMAL_DIGITS(self, s) -> str:
        return s

    def DECIMAL_DIGITS(self, s) -> str:
        return s

    @v_args(inline=True)
    def opt_sign(self, s: Optional[str]) -> PosOrNeg:
        return PosOrNeg.POS if s is None else PosOrNeg(s)

    @v_args(inline=True, meta=True)
    def number(self, meta: Meta, x: NumberAst):
        x.meta = meta
        return x

    @v_args(inline=True, meta=True)
    def exact(self, meta: Meta, x: Union[Int, Rational, ComplexExact]):
        x.meta = meta
        return x

    @v_args(inline=True, meta=True)
    def exact_integer_2(
            self, meta: Meta,
            _: str, sign: Optional[PosOrNeg], i: Int[Base.BINARY]
    ) -> Int[Base.BINARY]:
        value = i.value if sign and sign == PosOrNeg.POS else -i.value
        return Int(meta, Base.BINARY, value)

    @v_args(inline=True, meta=True)
    def exact_rational_2(
            self,
            meta: Meta,
            _: Optional[str],
            sign: PosOrNeg,
            unsigned_rational: UnsignedRational) -> RationalExact:
        return self.exact_rational(meta,
                                   Rational(Base.BINARY,
                                            sign,
                                            unsigned_rational.numerator,
                                            unsigned_rational.den))

    @v_args(inline=True, meta=True)
    def exact_rational_8(
            self,
            meta: Meta,
            _: Optional[str],
            sign: PosOrNeg,
            unsigned_rational: UnsignedRational) -> RationalExact:
        return self.exact_rational(meta,
                                   Rational(sign,
                                            Base.OCTAL,
                                            unsigned_rational.num,
                                            unsigned_rational.denom))

    @v_args(inline=True, meta=True)
    def exact_rational_10(self, meta: Meta, _: Optional[str], sign: PosOrNeg,
                          unsigned_rational: UnsignedRational):
        return self.exact_rational(meta,
                                   Rational(sign, unsigned_rational.num,
                                            unsigned_rational.den))

    @v_args(inline=True, meta=True)
    def exact_rational_16(self, meta: Meta, _: Optional[str], sign: PosOrNeg,
                          unsigned_rational: UnsignedRational):
        return self.exact_rational(meta,
                                   Rational(sign, unsigned_rational.num,
                                            unsigned_rational.den))

    def unsigned_rational[B](
            self, meta: Meta,
            base: B, numerator: Int[B], denominator: Int[B]
    ) -> UnsignedRational[B]:
        return UnsignedRational(meta, base, numerator, denominator)

    @v_args(inline=True, meta=True)
    def unsigned_rational_2(
            self, meta: Meta,
            numerator: Int[Base.BINARY], denominator: Int[Base.BINARY]
    ) -> UnsignedRational:
        return self.unsigned_rational(meta, Base.BINARY, numerator, denominator)

    @v_args(inline=True, meta=True)
    def unsigned_rational_8(
            self, meta: Meta,
            numerator: Int[Base.OCTAL], denominator: Int[Base.OCTAL]
    ) -> UnsignedRational[Base.OCTAL]:
        return self.unsigned_rational(meta, Base.OCTAL, numerator, denominator)

    @v_args(inline=True, meta=True)
    def unsigned_rational_10(
            self, meta: Meta,
            numerator: Int[Base.DECIMAL], denominator: Int[Base.DECIMAL]
    ) -> UnsignedRational[Base.DECIMAL]:
        return self.unsigned_rational(meta, Base.DECIMAL, numerator, denominator)

    @v_args(inline=True, meta=True)
    def unsigned_rational_16(
            self, meta: Meta,
            numerator: Int[Base.HEXADECIMAL],
            denominator: Int[Base.HEXADECIMAL]
    ) -> UnsignedRational[Base.HEXADECIMAL]:
        return self.unsigned_rational(
            meta, Base.HEXADECIMAL, numerator, denominator)


    @v_args(inline=True, meta=True)
    def exact_complex(self, meta: Meta, complex: Complex) -> ComplexExact:
        return ComplexExact(meta, complex)

    @v_args(inline=True, meta=True)
    def exact_complex_2(
            self,
            meta: Meta,
            real: Optional[Rational],
            sign: PosOrNeg,
            imaginary: Optional[UnsignedRational]) -> ComplexExact:
        imag = Rational(sign, imaginary.num, imaginary.denom) \
            if imaginary else Rational.from_int(2, 1)
        return self.exact_complex(
            meta, Complex(real or Rational.from_int(2, 0), imag))

    @v_args(inline=True, meta=True)
    def exact_complex_8(
            self,
            meta: Meta,
            real: Optional[Rational],
            sign: PosOrNeg,
            imaginary: Optional[UnsignedRational]) -> ComplexExact:
        imag = Rational(sign, imaginary.num, imaginary.denom) \
            if imaginary else Rational.from_int(8, 1)
        return self.exact_complex(
            meta, Complex(real or Rational.from_int(8, 0), imag))

    @v_args(inline=True, meta=True)
    def exact_complex_10(
            self,
            meta: Meta,
            real: Optional[Rational],
            sign: PosOrNeg,
            imaginary: Optional[UnsignedRational]) -> ComplexExact:
        imag = Rational(sign, imaginary.num, imaginary.denom) \
            if imaginary else Rational.from_int(10, 1)
        return self.exact_complex(
            meta, Complex(real or Rational.from_int(10, 0), imag))

    @v_args(inline=True, meta=True)
    def exact_complex_16(
            self,
            meta: Meta,
            real: Optional[Rational],
            sign: PosOrNeg,
            imaginary: Optional[UnsignedRational]) -> ComplexExact:
        imag = Rational(sign, imaginary.num, imaginary.denom) \
            if imaginary else Rational.make(1, 1)
        return self.exact_complex(
            meta, Complex(real or Rational.from_int(16, 0), imag))

