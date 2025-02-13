from hypothesis import given, strategies as st

from pyracket.expr_ast import PyracketParser, Rational, ComplexExact
from ..ParserTestBase import ParserTestBase
from ..numbers import exact_prefixes, strip_base

class TestComplex(ParserTestBase):
    p = PyracketParser(start="number", propagate_positions=True)

