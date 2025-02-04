import decimal
import sys
from dataclasses import dataclass
from pathlib import Path

from lark import Lark, ast_utils, Transformer
from lark.tree import Meta

this_module = sys.modules[__name__]

@dataclass
class Int:
    value: int

@dataclass
class HexInt:
    value: int

@dataclass
class DecimalInt:
    value: int

@dataclass
class OctalInt:
    value: int

@dataclass
class BinaryInt:
    value: int

@dataclass
class Rational:
    is_negative: bool
    numerator: Int
    denominator: Int

class _Ast(ast_utils.Ast, ast_utils.WithMeta):
    pass


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
class ExactRational(_Ast):
    meta: Meta
    value: Rational



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
            if 0xD800 <= int(s[2:6]) <= 0xDBFF and 0xDC00 <= int(s[6:8]) <= 0xDFFF:
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

class PyracketParser(Lark):
    def __init__(self, **options) -> None:
        super().__init__(Path(__file__).with_name("pyracket.lark").read_text(), **options)

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