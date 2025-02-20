from .ParserTestBase import ParserTestBase
from pyracket.syntax import PyracketParser
from pyracket.syntax.expr_ast import BooleanAst


class TestBoolean(ParserTestBase):
    p = PyracketParser(start="boolean")

    def test_true(self):
        self.assert_parse_equal("#true", BooleanAst, True, 0, 5)

    def test_false(self):
        self.assert_parse_equal("#false", BooleanAst, False, 0, 6)
