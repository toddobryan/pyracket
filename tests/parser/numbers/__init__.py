import random

from hypothesis import strategies as st
from hypothesis.strategies import composite

from pyracket.semantics.numbers import BASE_TO_ALPH, Base, RkRational, \
    RkExactFloatingPoint, PosOrNeg, RkInteger, RkExactComplex

BASE_PREFIXES = {
    2 : ["#b", "#B"],
    8 : ["#o", "#O"],
    10 : ["", "#d", "#D"],
    16 : ["#x", "#X"],
}

def exact_prefixes(base:  Base) -> list[str]:
    prefixes = []
    for exact_prefix in ["", "#e", "#E"]:
        for base_prefix in BASE_PREFIXES[base.value]:
            prefixes.append(exact_prefix + base_prefix)
            if exact_prefix and base_prefix:
                prefixes.append(base_prefix + exact_prefix)
    return prefixes

def exp_mark(base: Base) -> list[str]:
    exp_marks = ["s", "S", "l", "L"]
    if base != Base.HEXADECIMAL:
        exp_marks.extend(["d", "D", "e", "E", "f", "F"])
    return exp_marks

@composite
def random_unsigned_int(draw, base: Base, include_zero=True) -> tuple[int, str]:
    if include_zero:
        int_string = draw(st.text(alphabet=BASE_TO_ALPH[base], min_size=1))
    else:
        first = draw(st.text(alphabet=BASE_TO_ALPH[base][1:], min_size=1, max_size=1))
        rest = draw(st.text(alphabet=BASE_TO_ALPH[base]))
        int_string = first + rest
    return int(int_string, base.value), int_string

@composite
def random_signed_int(draw, base: Base) -> tuple[int, str]:
    sign = draw(st.sampled_from(["", "-"]))
    int_string = sign + draw(st.text(alphabet=BASE_TO_ALPH[base], min_size=1))
    return int(int_string, base.value), int_string

@composite
def random_rational(draw, base: Base) -> tuple[RkRational, str]:
    num, num_str = draw(random_signed_int(base))
    den, den_str = draw(random_unsigned_int(base, include_zero=False))
    return RkRational(base, num, den), num_str + "/" + den_str

@composite
def random_floating_point(draw, base: Base, include_zero=True) -> tuple[RkExactFloatingPoint, str]:
    left, left_str = draw(random_signed_int(base))
    right, right_str = draw(random_unsigned_int(base), include_zero=include_zero)
    exp_num = None
    exp_mk = None
    exp_str = None
    if random.random() < 0.5:
        exp_mk = draw(st.sampled_from(exp_mark(base)))
        exp_num, exp_str = draw(random_signed_int, base)
    if left_str.startswith("-"):
        left = -left
        left_str = left_str[1:]
        sign = PosOrNeg.NEG
    else:
        sign = PosOrNeg.POS

    exp = RkInteger(base, exp_num or 0)
    if exp_mk and exp_num:
        exp_str_all = exp_mk + exp_str
    else:
        exp_str_all = ""
    return (RkExactFloatingPoint(base, sign, left_str + right_str, exp),
            left_str + "." + right_str + exp_str_all)

@composite
def random_complex(draw, base: Base) -> tuple[RkExactComplex, str]:
    real, real_str = draw(st.one_of(random_rational(base),
                                    random_floating_point(base)))
    imag, imag_str = draw(st.one_of(random_rational(base),
                                    random_floating_point(base)))
    i = draw(st.sampled_from(["i", "I"]))
    value = RkExactComplex(real, imag)
    sign = "" if imag_str.startswith("-") else "+"
    return value, real_str + sign + imag_str + i


EXACT = ["", "#e", "#E"]
DECIMAL = ["", "#d", "#D"]
BINARY = ["#b", "#B"]
OCTAL = ["#o", "#O"]
HEX = ["#x", "#X"]

def strip_base(s: str) -> str:
    if s.startswith("-"):
        return s[0] + s[3:]
    else:
        return s[2:]
