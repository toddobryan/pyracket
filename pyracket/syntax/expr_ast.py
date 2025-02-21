import sys
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Optional

from lark import ast_utils
from lark.visitors import Transformer, v_args
from lark.tree import Meta

from pyracket.semantics.numbers import Base, RkNumber, RkExact, RkExactReal, \
    RkInteger, RkRational, RkExactFloatingPoint, RkExactComplex

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


class PosOrNeg(Enum):
    POS = "+"
    NEG = "-"


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
    meta: Meta
    base: B
    value: R


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
    value: RkExactFloatingPoint


@dataclass
class ExactComplexAst[B](NumberAst[RkExactComplex]):
    meta: Meta
    base: B
    value: RkExactComplex


def integer_ast_of[B](
        meta: Meta, base: B, sign: Optional[PosOrNeg], digits: str
) -> IntegerAst[B]:
    print(f"digits: {digits}")
    value = int(digits, base.value)
    value = -value if sign is PosOrNeg.NEG else value
    return IntegerAst(meta, base, RkInteger(base, value))

def rational_ast_of[B](
        meta: Meta, base: B, sign: Optional[PosOrNeg], value: RkRational
) -> RationalAst[B]:
    if sign is PosOrNeg.NEG:
        value = RkRational(-value.numerator, value.denominator)
    return RationalAst(meta, base, value)

class ToAstExpr(Transformer):
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
    def exact_real[R](self, value: ExactRealAst[R]) -> ExactRealAst[R]:
        return value

    @v_args(inline=True)
    def exact_integer(self, value: IntegerAst[B]) -> IntegerAst[B]:
        return value

    @v_args(inline=True, meta=True)
    def exact_integer_2(
            self, meta: Meta, _: str, sign: Optional[PosOrNeg], digits: str
    ) -> IntegerAst[Base.BINARY]:
        return integer_ast_of(meta, Base.BINARY, sign, digits)

    @v_args(inline=True, meta=True)
    def exact_integer_8(
            self, meta: Meta, _: str, sign: Optional[PosOrNeg], digits: str
    ) -> IntegerAst[Base.BINARY]:
        return integer_ast_of(meta, Base.OCTAL, sign, digits)

    @v_args(inline=True, meta=True)
    def exact_integer_10(
            self, meta: Meta, _: str, sign: Optional[PosOrNeg], digits: str
    ) -> IntegerAst[Base.BINARY]:
        return integer_ast_of(meta, Base.DECIMAL, sign, digits)

    @v_args(inline=True, meta=True)
    def exact_integer_16(
            self, meta: Meta, _: str, sign: Optional[PosOrNeg], digits: str
    ) -> IntegerAst[Base.BINARY]:
        return integer_ast_of(meta, Base.HEXADECIMAL, sign, digits)

    @v_args(inline=True)
    def exact_rational(self, value: RationalAst[B]) -> RationalAst:
        return value
    
    @v_args(inline=True, meta=True)
    def exact_rational_2(
        self, meta: Meta, _: str, sign: Optional[PosOrNeg], value: RkRational
    ) -> RationalAst[Base.BINARY]:
        return rational_ast_of(meta, Base.BINARY, sign, value)
    
    @v_args(inline=True, meta=True)
    def exact_rational_8(
        self, meta: Meta, _: str, sign: Optional[PosOrNeg], value: RkRational
    ) -> RationalAst[Base.OCTAL]:
        return rational_ast_of(meta, Base.OCTAL, sign, value)
    
    @v_args(inline=True, meta=True)
    def exact_rational_10(
        self, meta: Meta, _: str, sign: Optional[PosOrNeg], value: RkRational
    ) -> RationalAst[Base.DECIMAL]:
        return rational_ast_of(meta, Base.DECIMAL, sign, value)
    
    @v_args(inline=True, meta=True)
    def exact_rational_16(
        self, meta: Meta, _: str, sign: Optional[PosOrNeg], value: RkRational
    ) -> RationalAst[Base.HEXADECIMAL]:
        return rational_ast_of(meta, Base.HEXADECIMAL, sign, value)

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

    @v_args(inline=True)
    def unsigned_floating_point_2(
            self, before: str, after: str,
            exp: Optional[RkInteger[Base.BINARY]]
    ) -> RkExactFloatingPoint:
        return RkExactFloatingPoint(
            Base.BINARY,
            RkInteger(Base.BINARY, int(before + after, 2)),
            exp if exp else RkInteger(Base.BINARY, 0)
        )

    @v_args(inline=True)
    def unsigned_floating_point_8(
            self, before: str, after: str,
            exp: Optional[RkInteger[Base.OCTAL]]
    ) -> RkExactFloatingPoint:
        return RkExactFloatingPoint(
            Base.OCTAL,
            RkInteger(Base.OCTAL, int(before + after, 8)),
            exp if exp else RkInteger(Base.OCTAL, 0)
        )

    @v_args(inline=True)
    def unsigned_floating_point_10(
            self, before: str, after: str,
            exp: Optional[RkInteger[Base.DECIMAL]]
    ) -> RkExactFloatingPoint:
        return RkExactFloatingPoint(
            Base.DECIMAL,
            RkInteger(Base.DECIMAL, int(before + after, 10)),
            exp if exp else RkInteger(Base.DECIMAL, 0)
        )

    @v_args(inline=True)
    def unsigned_floating_point_16(
            self, before: str, after: str,
            exp: Optional[RkInteger[Base.HEXADECIMAL]]
    ) -> RkExactFloatingPoint:
        return RkExactFloatingPoint(
            Base.HEXADECIMAL,
            RkInteger(Base.HEXADECIMAL, int(before + after, 16)),
            exp if exp else RkInteger(Base.HEXADECIMAL, 0)
        )
    
 
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
