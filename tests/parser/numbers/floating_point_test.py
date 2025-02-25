from decimal import Decimal
from typing import Tuple

from hypothesis import given, strategies as st, example

from pyracket.semantics.numbers import BASE_TO_ALPH, Base, RkExactFloatingPoint, \
    RkInteger, PosOrNeg
from pyracket.syntax import PyracketParser
from pyracket.syntax.expr_ast import ExactFloatingPointAst
from tests.parser.ParserTestBase import ParserTestBase
from tests.parser.numbers import exact_prefixes


class TestFloatingPoint(ParserTestBase):
    p = PyracketParser(start="number")

    @given(
        st.sampled_from(exact_prefixes(10)),
        st.decimals(allow_nan=False, allow_infinity=False)
    )
    def test_random_decimals(self, prefix: str, d: Decimal):
        prefix = ""
        if "." not in str(d): # handle integers elsewhere
            return
        decimal = str(d)
        to_parse = prefix + decimal
        sign_plus_left, right_plus_exp = decimal.split(".")
        sign, left = split_sign(sign_plus_left)
        if "E" in right_plus_exp:
            right, exp = right_plus_exp.split("E")
        else:
            right, exp = right_plus_exp, None
        digits = left + right
        exponent = RkInteger(
            Base.DECIMAL, int(exp) if exp else -len(right)
        )
        result = self.assert_parse_equal(
            to_parse, ExactFloatingPointAst,
            RkExactFloatingPoint(Base.DECIMAL, sign, digits, exponent),
            0, len(to_parse))
        print(f"{type(result.value.dec)}, {type(d)}")
        print(f"{result.value.dec} == {d}")
        assert result.value.dec == d

    @given(
        st.sampled_from(exact_prefixes(10)),
        st.text(alphabet=BASE_TO_ALPH[Base.DECIMAL]),
        st.text(BASE_TO_ALPH[Base.DECIMAL])
    )
    def test_random_decimal_strings(self, prefix, left, right):
        # "." is not a legal decimal number
        if not left and not right:
            return
        to_parse = prefix + left + "." + right
        digits = int(left + right)
        exponent = str(-len(right))
        self.assert_parse_equal(
            to_parse, ExactFloatingPointAst,
            RkExactFloatingPoint(10, digits, exponent), 0, len(to_parse))

    @given(st.sampled_from(exact_prefixes(2)), st.text(alphabet=BASE_TO_ALPH[Base.BINARY]), st.text(BASE_TO_ALPH[Base.BINARY]))
    def test_random_binary_strings(self, prefix, left, right):
        # "." is not a legal binary number
        if not left and not right:
            return
        to_parse = prefix + left + "." + right
        digits = int(left + right, 2)
        exponent = str(-len(right))
        self.assert_parse_equal(
            to_parse, ExactFloatingPointAst,
            RkExactFloatingPoint(2, digits, exponent), 0, len(to_parse))

def split_sign(s: str) -> Tuple[PosOrNeg, str]:
    if s[0] in "+-":
        return PosOrNeg.POS if s[0] == "+" else PosOrNeg.NEG, s[1:]
    else:
        return PosOrNeg.POS, s