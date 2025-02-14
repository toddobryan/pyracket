import sys
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Optional

from lark import ast_utils
from lark.visitors import Transformer, v_args
from lark.tree import Meta

from pyracket.semantics.numbers import RkNumber, RkExact, RkExactReal, \
    RkInteger, RkRational, RkExactFloatingPoint, RkExactComplex

this_module = sys.modules[__name__]

class PyracketAst[T](ast_utils.Ast, ast_utils.WithMeta):
    meta: Meta
    value: T

@dataclass
class StringAst(PyracketAst[str], ast_utils.AsList):
    meta: Meta
    value: str

    def __init__(self, meta: Meta, value: list[str]) -> None:
        super().__init__()
        self.meta = meta
        self.value = "".join(value)


@dataclass
class BooleanAst(PyracketAst[bool]):
    meta: Meta
    value: bool

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
    value = int(digits, base.value)
    value = -value if sign is PosOrNeg.NEG else value
    return IntegerAst(meta, base, RkInteger(value))
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
