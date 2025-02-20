from pyracket.syntax import PyracketParser
from ..ParserTestBase import ParserTestBase


class TestComplex(ParserTestBase):
    p = PyracketParser(start="number")

