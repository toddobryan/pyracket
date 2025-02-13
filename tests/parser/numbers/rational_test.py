from hypothesis import given, strategies as st

from pyracket.expr_ast import PyracketParser, RationalExact, Rational
from ..ParserTestBase import ParserTestBase
from ..numbers import exact_prefixes, strip_base


class TestRational(ParserTestBase):
    p = PyracketParser(start="number", propagate_positions=True)

    @given(st.sampled_from(exact_prefixes(10)), st.integers(), st.integers(min_value=1))
    def test_random_decimal_fractions(self, prefix, num, den):
        to_parse = "".join(prefix) + str(num) + "/" + str(den)
        self.assert_parse_equal(
            to_parse, RationalExact,
            Rational.make(10, num, den), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(2)), st.integers(), st.integers(min_value=1))
    def test_random_binary_fractions(self, prefix, num, den):
        to_parse = prefix + strip_base(bin(num)) + "/" + strip_base(bin(den))
        self.assert_parse_equal(
            to_parse, RationalExact,
            Rational.make(2, num, den), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(8)), st.integers(), st.integers(min_value=1))
    def test_random_octal_fractions(self, prefix, num, den):
        to_parse = prefix + strip_base(oct(num)) + "/" + strip_base(oct(den))
        self.assert_parse_equal(to_parse, RationalExact,
                                Rational.make(8, num, den), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(16)), st.integers(), st.integers(min_value=1))
    def test_random_hex_fractions(self, prefix, num, den):
        to_parse = prefix + strip_base(hex(num)) + "/" + strip_base(hex(den))
        self.assert_parse_equal(to_parse, RationalExact,
                                Rational.make(16, num, den), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(10)), st.decimals(allow_nan=False, allow_infinity=False))
    def test_random_decimals(self, prefix, d):
        decimal = str(d)
        if "." not in decimal or "E" in decimal:
            pass # handled in integer and inexact
        else:
            to_parse = prefix + decimal
            left, right = decimal.split(".")
            num = int(left + right)
            den = 10 ** len(right)
            self.assert_parse_equal(
                to_parse, RationalExact,
                Rational.make(10, num, den), 0, len(to_parse))