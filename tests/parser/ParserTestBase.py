from typing import TypeVar, cast

from pyracket.syntax import PyracketParser

T = TypeVar("T")

class ParserTestBase:
    p: PyracketParser

    def assert_parse_equal(self, to_parse: str, cls: type[T], value, start, end):
        result = cast(cls, self.p.parse_ast(to_parse))
        print(f"RESULT: {result}\nVALUE: {value}")
        assert isinstance(result, cls)
        assert result.value == value
        assert result.meta.start_pos == start
        assert result.meta.end_pos == end
