from pyracket.syntax.expr_ast import BooleanAst, PyracketParser
from tests.parser.ParserTestBase import ParserTestBase


class TestBoolean(ParserTestBase):
    p = PyracketParser(start="boolean", propagate_positions=True)

    def test_true(self):
        self.assert_parse_equal("#true", BooleanAst, True, 0, 5)

    def test_false(self):
        self.assert_parse_equal("#false", BooleanAst, False, 0, 6)
