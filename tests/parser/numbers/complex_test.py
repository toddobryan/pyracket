import base64

from pyracket.semantics.numbers import Base
from pyracket.syntax import PyracketParser
from pyracket.syntax.expr_ast import ExactComplexAst
from . import exact_prefixes, random_complex
from ..ParserTestBase import ParserTestBase

from hypothesis import given, strategies as st

class TestComplex(ParserTestBase):
    p = PyracketParser(start="number")

    @given(st.sampled_from(exact_prefixes(Base.BINARY)), random_complex(Base.BINARY))
    def test_complex(self, prefix, res_plus_str):
        res, rand_str = res_plus_str
        to_parse = prefix + rand_str
        self.assert_parse_equal(
            to_parse, ExactComplexAst,
            res, 0, len(to_parse)
        )