from pyracket.expr_ast import Boolean, PyracketParser
from .ParserTestBase import ParserTestBase

class TestBoolean(ParserTestBase):
    p = PyracketParser(start="boolean", propagate_positions=True)

    def test_true(self):
        self.assert_parse_equal("#true", Boolean, True, 0, 5)

    def test_false(self):
        self.assert_parse_equal("#false", Boolean, False, 0, 6)
