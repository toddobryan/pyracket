from hypothesis import given, strategies as st

from pyracket.semantics.numbers import RkRational, Base
from pyracket.syntax import PyracketParser
from pyracket.syntax.expr_ast import RationalAst
from ..ParserTestBase import ParserTestBase
from ..numbers import exact_prefixes, strip_base, random_rational


class TestRational(ParserTestBase):
    p = PyracketParser(start="number")

    @given(st.sampled_from(exact_prefixes(Base.DECIMAL)), st.integers(), st.integers(min_value=1))
    def test_random_decimal_fractions(self, prefix, num, den):
        to_parse = "".join(prefix) + str(num) + "/" + str(den)
        self.assert_parse_equal(
            to_parse, RationalAst,
            RkRational(Base.DECIMAL, num, den), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(Base.BINARY)), st.integers(), st.integers(min_value=1))
    def test_random_binary_fractions(self, prefix, num, den):
        to_parse = prefix + strip_base(bin(num)) + "/" + strip_base(bin(den))
        self.assert_parse_equal(
            to_parse, RationalAst,
            RkRational(Base.BINARY, num, den), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(Base.OCTAL)), st.integers(), st.integers(min_value=1))
    def test_random_octal_fractions(self, prefix, num, den):
        to_parse = prefix + strip_base(oct(num)) + "/" + strip_base(oct(den))
        self.assert_parse_equal(
            to_parse, RationalAst,
            RkRational(Base.OCTAL, num, den), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(Base.HEXADECIMAL)), st.integers(), st.integers(min_value=1))
    def test_random_hex_fractions(self, prefix, num, den):
        to_parse = prefix + strip_base(hex(num)) + "/" + strip_base(hex(den))
        self.assert_parse_equal(
            to_parse, RationalAst,
            RkRational(Base.HEXADECIMAL, num, den), 0, len(to_parse))

    def random_rational_template(self, base: Base, res: RkRational, to_parse: str):
        self.assert_parse_equal(
            to_parse, RationalAst,
            res, 0, len(to_parse),
        )

    @given(random_rational(Base.BINARY))
    def random_binary_rationals(self, rat_plus_str: tuple[RkRational, str]):
        self.random_rational_template(Base.BINARY, rat_plus_str[0], rat_plus_str[1])

    @given(random_rational(Base.OCTAL))
    def random_octal_rationals(self, rat_plus_str: tuple[RkRational, str]):
        self.random_rational_template(Base.OCTAL, rat_plus_str[0], rat_plus_str[1])

    @given(random_rational(Base.DECIMAL))
    def random_decimal_rationals(self, rat_plus_str: tuple[RkRational, str]):
        self.random_rational_template(Base.DECIMAL, rat_plus_str[0], rat_plus_str[1])

    @given(random_rational(Base.HEXADECIMAL))
    def random_hexadecimal_rationals(self, rat_plus_str: tuple[RkRational, str]):
        self.random_rational_template(Base.HEXADECIMAL, rat_plus_str[0], rat_plus_str[1])

