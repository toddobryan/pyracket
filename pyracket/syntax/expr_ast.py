import sys
from dataclasses import dataclass
from importlib import resources as impres
from pathlib import Path
from typing import TypeVar, Generic

from lark import Lark, ast_utils, Transformer
from lark.tree import Meta

from .. import grammars

this_module = sys.modules[__name__]

T = TypeVar("T")

class PyracketAst(Generic[T], ast_utils.Ast, ast_utils.WithMeta):
    meta: Meta
    value: T


@dataclass
class StringAst(PyracketAst, ast_utils.AsList):
    meta: Meta
    value: str

    def __init__(self, meta: Meta, value: list[str]) -> None:
        super().__init__()
        self.meta = meta
        self.value = "".join(value)


@dataclass
class BooleanAst(PyracketAst):
    meta: Meta
    value: bool


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


transformer = ast_utils.create_transformer(this_module, ToAst())


class PyracketParser(Lark):
    def __init__(self, **options) -> None:
        super().__init__(
            (impres.files(grammars) / "expr.lark").read_text(), **options)

    def parse_ast(self, text: str) -> ast_utils.Ast:
        tree = self.parse(text)
        return transformer.transform(tree)

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
