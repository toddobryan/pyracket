import decimal
from enum import Enum
import sys
from dataclasses import dataclass
from numbers import Rational
from pathlib import Path
from typing import Optional, TypeVar, Generic, Union

from lark import Lark, ast_utils, Transformer, v_args, Token
from lark.tree import Meta

this_module = sys.modules[__name__]

T = TypeVar("T")


class Base(Enum):
    BINARY = 2
    OCTAL = 8
    DECIMAL = 10
    HEXADECIMAL = 16


class _Ast(Generic[T], ast_utils.Ast, ast_utils.WithMeta):
    meta: Meta
    value: T


class NumberAst(_Ast):
    pass


class ExactAst(NumberAst):
    pass


class Int:
    value: int


@dataclass
class HexInt(Int):
    value: int


@dataclass
class DecimalInt(Int):
    value: int


@dataclass
class OctalInt(Int):
    value: int


@dataclass
class BinaryInt(Int):
    value: int


class PosOrNeg(Enum):
    POS = "+"
    NEG = "-"

    @staticmethod
    def of(i: int) -> "PosOrNeg":
        return PosOrNeg.POS if i >= 0 else PosOrNeg.NEG


base_to_class: dict[int, type[Int]] = {
    2: BinaryInt,
    8: OctalInt,
    10: DecimalInt,
    16: HexInt,
}


@dataclass
class Rational(NumberAst):
    pos_or_neg: PosOrNeg
    numerator: Int
    denominator: Int

    @staticmethod
    def make(base: int, numerator: int, denominator: int) -> Rational:
        pos_or_neg = PosOrNeg.POS \
            if PosOrNeg.of(numerator) == PosOrNeg.of(denominator) \
            else PosOrNeg.NEG
        if base == 2:
            return Rational(
                pos_or_neg,
                BinaryInt(abs(numerator)),
                BinaryInt(abs(denominator)))
        elif base == 8:
            return Rational(
                pos_or_neg,
                OctalInt(abs(numerator)),
                OctalInt(abs(denominator)))
        elif base == 10:
            return Rational(
                pos_or_neg,
                DecimalInt(abs(numerator)),
                DecimalInt(abs(denominator)))
        elif base == 16:
            return Rational(
                pos_or_neg,
                HexInt(abs(numerator)),
                HexInt(abs(denominator)))
        else:
            raise ValueError(f"Invalid base: {base}")

    @staticmethod
    def from_int(base: int, num: int) -> Rational:
        return Rational.make(base, num, 1)


@dataclass
class Complex(NumberAst):
    real: Rational
    imaginary: Rational


@dataclass
class ComplexExact(NumberAst):
    meta: Meta
    value: Complex


@dataclass
class String(_Ast, ast_utils.AsList):
    meta: Meta
    value: str

    def __init__(self, meta: Meta, value: list[str]) -> None:
        super().__init__()
        self.meta = meta
        self.value = "".join(value)


@dataclass
class Boolean(_Ast):
    meta: Meta
    value: bool


@dataclass
class RationalExact(NumberAst):
    meta: Meta
    value: Rational


@dataclass
class UnsignedRational(NumberAst):
    meta: Meta
    numerator: Int
    denominator: Int


@dataclass
class Sign(_Ast):
    meta: Meta
    value: PosOrNeg

    def __init__(self, meta: Meta, value: Optional[str]) -> None:
        self.meta = meta
        self.value = PosOrNeg.POS if value is None else PosOrNeg(value)


class ToAst(Transformer):
    def TRUE(self, s):
        return True

    def FALSE(self, s):
        return False

    def UNESCAPED_CHAR(self, s) -> str:
        return s[0]

    def ESCAPED_CHAR(self, s) -> str:
        assert s[0] == "\\"
        if s[1] in escape_chars:
            return escape_chars[s[1]]
        elif s[1] in "01234567":
            return chr(int(s[1:], 8))
        elif s[1] == "x":
            return chr(int(s[2:], 16))
        elif s[1] == "u" and "\\u" not in s[2:]:
            return chr(int(s[2:], 16))
        elif s[1] == "u" and s[6:8] == "\\u":
            if 0xD800 <= int(s[2:6]) <= 0xDBFF and 0xDC00 <= int(
                    s[6:8]) <= 0xDFFF:
                return chr(int(s[2:6], 16)) + chr(int(s[6:8], 16))
            else:
                raise ValueError(f"Invalid escape sequence: {s}")
        elif s[1] == "U":
            return chr(int(s[2:], 16))
        else:
            raise ValueError(f"Invalid escape sequence: {s}")

    def UNSIGNED_INTEGER_2(self, s) -> Int:
        return BinaryInt(int(s, 2))

    def UNSIGNED_INTEGER_8(self, s) -> Int:
        return OctalInt(int(s, 8))

    def UNSIGNED_INTEGER_10(self, s) -> Int:
        return DecimalInt(int(s))

    def UNSIGNED_INTEGER_16(self, s) -> Int:
        return HexInt(int(s, 16))

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
    def exact(self, meta: Meta, x: Union[Rational, ComplexExact]):
        x.meta = meta
        return x

    @v_args(inline=True, meta=True)
    def exact_rational(self,
                       meta: Meta,
                       _: Optional[str],
                       sign: PosOrNeg,
                       unsigned_rational: UnsignedRational):
        return RationalExact(meta,
                             Rational(sign,
                                      unsigned_rational.numerator,
                                      unsigned_rational.denominator))

    @v_args(inline=True, meta=True)
    def exact_rational_2(
            self,
            meta: Meta,
            _: Optional[str],
            sign: PosOrNeg,
            unsigned_rational: UnsignedRational) -> RationalExact:
        return self.exact_rational(meta,
                                   Rational(sign,
                                            unsigned_rational.numerator,
                                            unsigned_rational.denominator))

    @v_args(inline=True, meta=True)
    def exact_rational_8(
            self,
            meta: Meta,
            _: Optional[str],
            sign: PosOrNeg,
            unsigned_rational: UnsignedRational) -> RationalExact:
        return self.exact_rational(meta,
                                   Rational(sign,
                                            unsigned_rational.numerator,
                                            unsigned_rational.denominator))

    @v_args(inline=True, meta=True)
    def exact_rational_10(self, meta: Meta, _: Optional[str], sign: PosOrNeg,
                          unsigned_rational: UnsignedRational):
        return self.exact_rational(meta,
                                   Rational(sign, unsigned_rational.numerator,
                                            unsigned_rational.denominator))

    @v_args(inline=True, meta=True)
    def exact_rational_16(self, meta: Meta, _: Optional[str], sign: PosOrNeg,
                          unsigned_rational: UnsignedRational):
        return self.exact_rational(meta,
                                   Rational(sign, unsigned_rational.numerator,
                                            unsigned_rational.denominator))

    def unsigned_rational(self, meta: Meta, numerator: Int,
                          denominator: Optional[Int]) -> UnsignedRational:
        return UnsignedRational(meta, numerator, denominator)

    @v_args(inline=True, meta=True)
    def unsigned_rational_2(self, meta: Meta, numerator: Int,
                            denominator: Optional[Int]) -> UnsignedRational:
        return self.unsigned_rational(meta, numerator,
                                      denominator or BinaryInt(1))

    @v_args(inline=True, meta=True)
    def unsigned_rational_8(self, meta: Meta, numerator: Int,
                            denominator: Optional[Int]) -> UnsignedRational:
        return self.unsigned_rational(meta, numerator,
                                      denominator or OctalInt(1))

    @v_args(inline=True, meta=True)
    def unsigned_rational_10(self, meta: Meta, numerator: DecimalInt,
                             denominator: Optional[
                                 DecimalInt]) -> UnsignedRational:
        return self.unsigned_rational(meta, numerator,
                                      denominator or DecimalInt(1))

    @v_args(inline=True, meta=True)
    def unsigned_rational_16(self, meta: Meta, numerator: Int,
                             denominator: Optional[Int]) -> UnsignedRational:
        return self.unsigned_rational(meta, numerator, denominator or HexInt(1))

    @v_args(inline=True, meta=True)
    def unsigned_decimal(self, meta: Meta, s: str) -> UnsignedRational:
        left, right = s.split(".")
        num = DecimalInt(int(left + right))
        den = DecimalInt(10 ** len(right))
        return self.unsigned_rational(meta, num, den)

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
        imag = Rational(sign, imaginary.numerator, imaginary.denominator) \
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
        imag = Rational(sign, imaginary.numerator, imaginary.denominator) \
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
        imag = Rational(sign, imaginary.numerator, imaginary.denominator) \
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
        imag = Rational(sign, imaginary.numerator, imaginary.denominator) \
            if imaginary else Rational.make(1, 1)
        return self.exact_complex(
            meta, Complex(real or Rational.from_int(16, 0), imag))


class PyracketParser(Lark):
    def __init__(self, **options) -> None:
        super().__init__(Path(__file__).with_name("pyracket.lark").read_text(),
                         **options)

    def parse_ast(self, text: str) -> ast_utils.Ast:
        tree = self.parse(text)
        return transformer.transform(tree)


transformer = ast_utils.create_transformer(this_module, ToAst())

escape_chars = {
    "a": "\a",
    "b": "\b",
    "e": "\033",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
    '"': '"',
    "'": "'",
    "\\": "\\",
}
