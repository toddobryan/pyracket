from decimal import Decimal
from typing import Tuple

from hypothesis import given, strategies as st

from pyracket.semantics.numbers import BASE_TO_ALPH, Base, RkExactFloatingPoint, \
    RkInteger, PosOrNeg
from pyracket.syntax import PyracketParser
from pyracket.syntax.expr_ast import ExactFloatingPointAst
from tests.parser.ParserTestBase import ParserTestBase
from tests.parser.numbers import exact_prefixes


class TestFloatingPoint(ParserTestBase):
    p = PyracketParser(start="number")

    @given(
        st.sampled_from(exact_prefixes(Base.DECIMAL)),
        st.decimals(allow_nan=False, allow_infinity=False)
    )
    def test_random_decimals(self, prefix: str, d: Decimal):
        dec = str(d)
        if "." not in dec: # handle integers elsewhere
            return
        to_parse = prefix + dec
        print(f"TRYING: {to_parse}")
        sign_plus_left, right_plus_exp = dec.split(".")
        sign, left = split_sign(sign_plus_left)
        if "E" in right_plus_exp:
            right, exp = right_plus_exp.split("E")
        else:
            right, exp = right_plus_exp, None
        digits = left + right
        exponent = RkInteger(
            Base.DECIMAL, int(exp) - len(right) if exp else -len(right)
        )
        result = self.assert_parse_equal(
            to_parse, ExactFloatingPointAst,
            RkExactFloatingPoint(Base.DECIMAL, sign, digits, exponent),
            0, len(to_parse))
        print(f"{type(result.value.dec())}, {type(d)}")
        print(f"{repr(result.value.dec())} == {repr(d)}")
        assert result.value.dec() == d

    def random_string_template(
            self,
            base: Base,
            prefix: str,
            sign: str,
            left: str,
            right: str,
    ) -> None:
        # "." is not a legal decimal number
        if not left and not right:
            return
        to_parse = prefix + sign + left + "." + right
        pos_or_neg, mult = \
            (PosOrNeg.NEG, -1) if sign == "-" else (PosOrNeg.POS, 1)
        digits = left + right
        exponent = RkInteger(base, -len(right))
        result = self.assert_parse_equal(
            to_parse, ExactFloatingPointAst,
            RkExactFloatingPoint(base, pos_or_neg, digits, exponent),
            0, len(to_parse)
        )
        assert (result.value.dec() == Decimal(mult)
                * Decimal(int(digits, base.value))
                * Decimal(base.value) ** Decimal(exponent.value))

    @given(
        st.sampled_from(exact_prefixes(Base.BINARY)),
        st.sampled_from(["", "+", "-"]),
        st.text(alphabet=BASE_TO_ALPH[Base.BINARY]),
        st.text(BASE_TO_ALPH[Base.BINARY]),
    )
    def test_random_binary_strings(self, prefix, sign, left, right):
        self.random_string_template(Base.BINARY, prefix, sign, left, right)

    @given(
        st.sampled_from(exact_prefixes(Base.OCTAL)),
        st.sampled_from(["", "+", "-"]),
        st.text(alphabet=BASE_TO_ALPH[Base.BINARY]),
        st.text(BASE_TO_ALPH[Base.BINARY]),
    )
    def test_random_octal_strings(self, prefix, sign, left, right):
        self.random_string_template(Base.OCTAL, prefix, sign, left, right)


    @given(
        st.sampled_from(exact_prefixes(Base.DECIMAL)),
        st.sampled_from(["", "+", "-"]),
        st.text(alphabet=BASE_TO_ALPH[Base.BINARY]),
        st.text(BASE_TO_ALPH[Base.BINARY]),
    )
    def test_random_decimal_strings(self, prefix, sign, left, right):
        self.random_string_template(Base.DECIMAL, prefix, sign, left, right)

    @given(
        st.sampled_from(exact_prefixes(Base.HEXADECIMAL)),
        st.sampled_from(["", "+", "-"]),
        st.text(alphabet=BASE_TO_ALPH[Base.BINARY]),
        st.text(BASE_TO_ALPH[Base.BINARY]),
    )
    def test_random_hex_strings(self, prefix, sign, left, right):
        self.random_string_template(Base.HEXADECIMAL, prefix, sign, left, right)



def split_sign(s: str) -> Tuple[PosOrNeg, str]:
    if s[0] in "+-":
        return PosOrNeg.POS if s[0] == "+" else PosOrNeg.NEG, s[1:]
    else:
        return PosOrNeg.POS, s