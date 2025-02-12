import unittest
from typing import TypeVar, cast

from pyracket.create_ast import _Ast
from pyracket.pyracket_ast import PyracketParser

T = TypeVar("T")

class ParserTestBase():
    p: PyracketParser

    def assert_parse_equal(self, to_parse: str, cls: type[T], value, start, end):
        result = cast(cls, self.p.parse_ast(to_parse))
        assert isinstance(result, cls)
        assert result.value == value
        assert result.meta.start_pos == start
        assert result.meta.end_pos == end
