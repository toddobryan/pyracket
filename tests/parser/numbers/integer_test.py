from hypothesis import given, strategies as st, example

from pyracket.semantics.numbers import RkInteger, Base
from pyracket.syntax import PyracketParser
from pyracket.syntax.expr_ast import IntegerAst
from tests.parser.ParserTestBase import ParserTestBase
from . import strip_base, random_signed_int

from ..numbers import exact_prefixes

class TestInteger(ParserTestBase):
    p = PyracketParser(start="exact_integer")

    def test_zero(self):
        self.assert_parse_equal(
            "0", IntegerAst,
            RkInteger(Base.DECIMAL, 0), 0, 1)

    @given(st.sampled_from(exact_prefixes(Base.DECIMAL)), st.integers())
    @example("", 0)
    @example("#e", 1)
    @example("#e#d", -1)
    def test_random_decimal_integers(self, prefix, i):
        to_parse = prefix + str(i)
        self.assert_parse_equal(
            to_parse, IntegerAst,
            RkInteger(Base.DECIMAL, i), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(Base.BINARY)), st.integers())
    def test_random_binary_integers(self, prefix, i):
        to_parse = prefix + strip_base(bin(i))
        self.assert_parse_equal(
            to_parse, IntegerAst,
            RkInteger(Base.BINARY, i), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(Base.OCTAL)), st.integers())
    def test_random_octal_integers(self, prefix, i):
        to_parse = prefix + strip_base(oct(i))
        self.assert_parse_equal(
            to_parse, IntegerAst,
            RkInteger(Base.OCTAL, i), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(Base.HEXADECIMAL)), st.integers())
    def test_random_hex_integers(self, prefix, i):
        to_parse = prefix + strip_base(hex(i))
        self.assert_parse_equal(
            to_parse, IntegerAst,
            RkInteger(Base.HEXADECIMAL, i), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(Base.BINARY)), random_signed_int(Base.BINARY))
    def test_random_binary_strings(self, prefix, res_plus_str):
        res, rand_str = res_plus_str
        to_parse = prefix + rand_str
        self.assert_parse_equal(
            to_parse, IntegerAst,
            RkInteger(Base.BINARY, res), 0, len(to_parse)
        )

    @given(st.sampled_from(exact_prefixes(Base.OCTAL)), random_signed_int(Base.OCTAL))
    def test_random_octal_strings(self, prefix, res_plus_str):
        res, rand_str = res_plus_str
        to_parse = prefix + rand_str
        self.assert_parse_equal(
            to_parse, IntegerAst,
            RkInteger(Base.OCTAL, res), 0, len(to_parse)
        )

    @given(st.sampled_from(exact_prefixes(Base.DECIMAL)), random_signed_int(Base.DECIMAL))
    def test_random_decimal_strings(self, prefix, res_plus_str):
        res, rand_str = res_plus_str
        to_parse = prefix + rand_str
        self.assert_parse_equal(
            to_parse, IntegerAst,
            RkInteger(Base.DECIMAL, res), 0, len(to_parse)
        )

    @given(st.sampled_from(exact_prefixes(Base.HEXADECIMAL)), random_signed_int(Base.HEXADECIMAL))
    def test_random_hex_strings(self, prefix, res_plus_str):
        res, rand_str = res_plus_str
        to_parse = prefix + rand_str
        self.assert_parse_equal(
            to_parse, IntegerAst,
            RkInteger(Base.HEXADECIMAL, res), 0, len(to_parse)
        )

