from pyracket.syntax.expr_ast import PyracketParser
from ..ParserTestBase import ParserTestBase


class TestComplex(ParserTestBase):
    p = PyracketParser(start="number", propagate_positions=True)

