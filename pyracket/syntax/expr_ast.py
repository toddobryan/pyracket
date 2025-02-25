import sys
from dataclasses import dataclass, replace
from typing import TypeVar, Optional, cast

from lark import ast_utils, Token
from lark.visitors import Transformer, v_args
from lark.tree import Meta

from pyracket.semantics.numbers import Base, RkNumber, RkExact, RkExactReal, \
    RkInteger, RkRational, RkExactFloatingPoint, RkExactComplex, PosOrNeg

this_module = sys.modules[__name__]

class PyracketAst[T](ast_utils.Ast, ast_utils.WithMeta):
    meta: Meta
    value: T

@dataclass
class StringAst(PyracketAst[str], ast_utils.AsList):
    meta: Meta
    value: str

    def __init__(self, meta: Meta, value: str) -> None:
        super().__init__()
        self.meta = meta
        self.value = "".join(value)


@dataclass
class BooleanAst(PyracketAst[bool]):
    meta: Meta
    value: bool

T = TypeVar("T")
N = TypeVar("N", bound=RkNumber)
E = TypeVar("E", bound=RkExact)
R = TypeVar("R", bound=RkExactReal)

class NumberAst[N](PyracketAst[N]):
    value: N


class ExactAst[E](NumberAst[E]):
    pass


class ExactRealAst[R](ExactAst[R]):
    meta: Meta
    value: R


@dataclass
class IntegerAst(ExactRealAst[RkInteger]):
    meta: Meta
    value: RkInteger


@dataclass
class RationalAst(ExactAst[RkRational]):
    meta: Meta
    value: RkRational


@dataclass
class ExactFloatingPointAst(ExactRealAst[RkExactFloatingPoint]):
    meta: Meta
    value: RkExactFloatingPoint


@dataclass
class ExactComplexAst(NumberAst[RkExactComplex]):
    meta: Meta
    value: RkExactComplex


def integer_ast_of(
        meta: Meta, base: Base, sign: Optional[PosOrNeg], digits: str
) -> IntegerAst:
    value = int(digits, base.value)
    value = -value if sign is PosOrNeg.NEG else value
    return IntegerAst(meta, RkInteger(base, value))

def rational_ast_of(
        meta: Meta, sign: Optional[PosOrNeg], value: RkRational
) -> RationalAst:
    if sign is PosOrNeg.NEG:
        value = RkRational(value.base, -value.numerator, value.denominator)
    return RationalAst(meta, value)

def unsigned_floating_point_of(
        base: Base, before: str, after: str, exp: Optional[RkInteger],
) -> RkExactFloatingPoint:
    eff_exp = RkInteger(base, exp.value if exp else 0 - len(after))
    return RkExactFloatingPoint(base, PosOrNeg.POS, before + after, eff_exp)

def exact_floating_point_ast_of(
        meta: Meta, sign: Optional[PosOrNeg], unsigned: RkExactFloatingPoint
) -> ExactFloatingPointAst:
    with_sign = RkExactFloatingPoint(
        unsigned.base,
        sign or PosOrNeg.POS,
        unsigned.digits,
        unsigned.exponent,
    )
    return ExactFloatingPointAst(meta, with_sign)

def to_exp(base: Base, sign: Optional[PosOrNeg], digits: str):

class ToAstExpr(Transformer):
    def TRUE(self, _: str):
        return True

    def FALSE(self, _: str):
        return False

    def UNESCAPED_CHAR(self, s: str) -> str:
        return s[0]

    def ESCAPED_CHAR(self, s: str) -> str:
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

    @v_args(inline=True)
    def opt_sign(self, sign: Optional[PosOrNeg]) -> Optional[PosOrNeg]:
        return sign

    def SIGN(self, s) -> PosOrNeg:
        return PosOrNeg(s[0])
        
    @v_args(inline=True, meta=True)
    def boolean(self, meta, value: bool) -> BooleanAst:
        return BooleanAst(meta, value)
    
    @v_args(inline=True, meta=True)
    def string(self, meta, *values: str) -> StringAst:
        return StringAst(meta, "".join(values))
    
    @v_args(inline=True)
    def number[N](self, value: NumberAst[N]) -> NumberAst[N]:
        return value

    @v_args(inline=True)
    def exact[E](self, value: ExactAst[E]) -> ExactAst[E]:
        return value

    @v_args(inline=True)
    def exact_real[R](self, value: ExactRealAst) -> ExactRealAst[R]:
        return value

    @v_args(inline=True)
    def exact_integer(self, value: IntegerAst) -> IntegerAst:
        return value

    @v_args(inline=True, meta=True)
    def exact_integer_2(
            self, meta: Meta, _: str, sign: Optional[PosOrNeg], digits: str
    ) -> IntegerAst:
        return integer_ast_of(meta, Base.BINARY, sign, digits)

    @v_args(inline=True, meta=True)
    def exact_integer_8(
            self, meta: Meta, _: str, sign: Optional[PosOrNeg], digits: str
    ) -> IntegerAst:
        return integer_ast_of(meta, Base.OCTAL, sign, digits)

    @v_args(inline=True, meta=True)
    def exact_integer_10(
            self, meta: Meta, _: str, sign: Optional[PosOrNeg], digits: str
    ) -> IntegerAst:
        return integer_ast_of(meta, Base.DECIMAL, sign, digits)

    @v_args(inline=True, meta=True)
    def exact_integer_16(
            self, meta: Meta, _: str, sign: Optional[PosOrNeg], digits: str
    ) -> IntegerAst:
        return integer_ast_of(meta, Base.HEXADECIMAL, sign, digits)

    @v_args(inline=True)
    def exact_rational(self, value: RationalAst) -> RationalAst:
        return value
    
    @v_args(inline=True, meta=True)
    def exact_rational_2(
        self, meta: Meta, _: str, sign: Optional[PosOrNeg], value: RkRational
    ) -> RationalAst:
        return rational_ast_of(meta, sign, value)
    
    @v_args(inline=True, meta=True)
    def exact_rational_8(
        self, meta: Meta, _: str, sign: Optional[PosOrNeg], value: RkRational
    ) -> RationalAst:
        return rational_ast_of(meta, sign, value)
    
    @v_args(inline=True, meta=True)
    def exact_rational_10(
        self, meta: Meta, _: str, sign: Optional[PosOrNeg], value: RkRational
    ) -> RationalAst:
        return rational_ast_of(meta, sign, value)
    
    @v_args(inline=True, meta=True)
    def exact_rational_16(
        self, meta: Meta, _: str, sign: Optional[PosOrNeg], value: RkRational
    ) -> RationalAst:
        return rational_ast_of(meta, sign, value)

    @v_args(inline=True)
    def unsigned_rational_2(self, num: str, den: str) -> RkRational:
        return RkRational(Base.BINARY, int(num, 2), int(den, 2))

    @v_args(inline=True)
    def unsigned_rational_8(self, num: str, den: str) -> RkRational:
        return RkRational(Base.OCTAL, int(num, 8), int(den, 8))

    @v_args(inline=True)
    def unsigned_rational_10(self, num: str, den: str) -> RkRational:
        return RkRational(Base.DECIMAL, int(num, 10), int(den, 10))

    @v_args(inline=True)
    def unsigned_rational_16(self, num: str, den: str) -> RkRational:
        return RkRational(Base.HEXADECIMAL, int(num, 16), int(den, 16))

    @v_args(inline=True)
    def exact_floating_point(
            self,
            value: ExactFloatingPointAst
    ) -> ExactFloatingPointAst:
        return value

    @v_args(inline=True, meta=True)
    def exact_floating_point_2(
            self, meta: Meta, _: str, sign: Optional[PosOrNeg],
            unsigned: RkExactFloatingPoint
    ) -> ExactFloatingPointAst:
        return exact_floating_point_ast_of(meta, sign, unsigned)

    @v_args(inline=True, meta=True)
    def exact_floating_point_8(
            self, meta: Meta, _: str, sign: Optional[PosOrNeg],
            unsigned: RkExactFloatingPoint
    ) -> ExactFloatingPointAst:
        return exact_floating_point_ast_of(meta, sign, unsigned)

    @v_args(inline=True, meta=True)
    def exact_floating_point_10(
            self, meta: Meta, _: str, sign: Optional[PosOrNeg],
            unsigned: RkExactFloatingPoint
    ) -> ExactFloatingPointAst:
        return exact_floating_point_ast_of(meta, sign, unsigned)

    @v_args(inline=True, meta=True)
    def exact_floating_point_16(
            self, meta: Meta, _: str, sign: Optional[PosOrNeg],
            unsigned: RkExactFloatingPoint
    ) -> ExactFloatingPointAst:
        return exact_floating_point_ast_of(meta, sign, unsigned)

    @v_args(inline=True)
    def unsigned_floating_point_2(
            self, before: str, after: str,
            exp: Optional[RkInteger]
    ) -> RkExactFloatingPoint:
        return unsigned_floating_point_of(Base.BINARY, before, after, exp)


    @v_args(inline=True)
    def unsigned_floating_point_8(
            self, before: str, after: str,
            exp: Optional[RkInteger]
    ) -> RkExactFloatingPoint:
        return unsigned_floating_point_of(Base.OCTAL, before, after, exp)

    @v_args(inline=True)
    def unsigned_floating_point_10(
            self, before: str, after: str, exp: Optional[RkInteger]
    ) -> RkExactFloatingPoint:
        return unsigned_floating_point_of(Base.DECIMAL, before, after, exp)

    @v_args(inline=True)
    def unsigned_floating_point_16(
            self, before: str, after: str,
            exp: Optional[RkInteger]
    ) -> RkExactFloatingPoint:
        return unsigned_floating_point_of(Base.HEXADECIMAL, before, after, exp)

    @v_args(inline=True)
    def star_2(self, *args: Token):
        return "".join([a.value for a in args])

    @v_args(inline=True)
    def star_8(self, *args: Token):
        return "".join([a.value for a in args])

    @v_args(inline=True)
    def star_10(self, *args: Token):
        return "".join([a.value for a in args])

    @v_args(inline=True)
    def star_16(self, *args: Token):
        return "".join([a.value for a in args])

    @v_args(inline=True)
    def plus_2(self, *args: Token):
        return "".join([a.value for a in args])

    @v_args(inline=True)
    def plus_8(self, *args: Token):
        return "".join([a.value for a in args])

    @v_args(inline=True)
    def plus_10(self, *args: Token):
        return "".join([a.value for a in args])

    @v_args(inline=True)
    def plus_16(self, *args: Token):
        return "".join([a.value for a in args])

    @v_args(inline=True)
    def exp_2(self, _: str, sign: Optional[PosOrNeg], power: str) -> RkInteger:
        return to_exp(Base.BINARY, sign, power)







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
