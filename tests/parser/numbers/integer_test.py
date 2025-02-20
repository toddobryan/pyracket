from hypothesis import given, strategies as st, example

from pyracket.semantics.numbers import RkInteger
from pyracket.syntax import PyracketParser
from pyracket.syntax.expr_ast import IntegerAst
from tests.parser.ParserTestBase import ParserTestBase
from . import strip_base

from ..numbers import exact_prefixes

class TestInteger(ParserTestBase):
    p = PyracketParser(start="exact_integer")

    def test_zero(self):
        self.assert_parse_equal(
            "0", IntegerAst,
            RkInteger(0), 0, 1)

    @given(st.sampled_from(exact_prefixes(10)), st.integers())
    @example("", 0)
    @example("#e", 1)
    @example("#e#d", -1)
    def test_random_decimal_integers(self, prefix, i):
        to_parse = prefix + str(i)
        self.assert_parse_equal(
            to_parse, IntegerAst,
            RkInteger(i), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(2)), st.integers())
    def test_random_binary_integers(self, prefix, i):
        to_parse = prefix + strip_base(bin(i))
        self.assert_parse_equal(
            to_parse, IntegerAst,
            RkInteger(i), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(8)), st.integers())
    def test_random_octal_integers(self, prefix, i):
        to_parse = prefix + strip_base(oct(i))
        self.assert_parse_equal(
            to_parse, IntegerAst,
            RkInteger(i), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(16)), st.integers())
    def test_random_hex_integers(self, prefix, i):
        to_parse = prefix + strip_base(hex(i))
        self.assert_parse_equal(
            to_parse, IntegerAst,
            RkInteger(i), 0, len(to_parse))