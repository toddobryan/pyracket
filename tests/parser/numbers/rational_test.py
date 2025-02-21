from hypothesis import given, strategies as st

from pyracket.semantics.numbers import RkRational, Base
from pyracket.syntax import PyracketParser
from pyracket.syntax.expr_ast import RationalAst
from ..ParserTestBase import ParserTestBase
from ..numbers import exact_prefixes, strip_base


class TestRational(ParserTestBase):
    p = PyracketParser(start="number")

    @given(st.sampled_from(exact_prefixes(10)), st.integers(), st.integers(min_value=1))
    def test_random_decimal_fractions(self, prefix, num, den):
        to_parse = "".join(prefix) + str(num) + "/" + str(den)
        self.assert_parse_equal(
            to_parse, RationalAst,
            RkRational(Base.DECIMAL, num, den), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(2)), st.integers(), st.integers(min_value=1))
    def test_random_binary_fractions(self, prefix, num, den):
        to_parse = prefix + strip_base(bin(num)) + "/" + strip_base(bin(den))
        self.assert_parse_equal(
            to_parse, RationalAst,
            RkRational(num, den), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(8)), st.integers(), st.integers(min_value=1))
    def test_random_octal_fractions(self, prefix, num, den):
        to_parse = prefix + strip_base(oct(num)) + "/" + strip_base(oct(den))
        self.assert_parse_equal(
            to_parse, RationalAst,
            RkRational(num, den), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(16)), st.integers(), st.integers(min_value=1))
    def test_random_hex_fractions(self, prefix, num, den):
        to_parse = prefix + strip_base(hex(num)) + "/" + strip_base(hex(den))
        self.assert_parse_equal(
            to_parse, RationalAst,
            RkRational(num, den), 0, len(to_parse))
