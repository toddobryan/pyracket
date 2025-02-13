from hypothesis import given, strategies as st, example
from pyracket.syntax.expr_ast import StringAst, PyracketParser
from tests.parser.ParserTestBase import ParserTestBase

class TestString(ParserTestBase):
    p = PyracketParser(start="string", propagate_positions=True)

    def test_hello(self):
        self.assert_parse_equal('"hello"', StringAst, "hello", 0, 7)

    def test_hello_world(self):
       self.assert_parse_equal('"hello world"', StringAst, "hello world", 0, 13)

    def test_hello_world_excl(self):
       self.assert_parse_equal('"hello world!"', StringAst, "hello world!", 0, 14)

    def test_empty_string(self):
        self.assert_parse_equal('""', StringAst, '', 0, 2)

    def test_single_quotes(self):
        self.assert_parse_equal('"0"', StringAst, '0', 0, 3)

    def test_tab(self):
        self.assert_parse_equal(r'"\t"', StringAst, '\t', 0, 4)

    def test_escape_quote(self):
        self.assert_parse_equal(r'"\""', StringAst, '"', 0, 4)

    def test_octal_char(self):
        self.assert_parse_equal(r'"\40"', StringAst, " ", 0, 5)

    def test_hex_char(self):
        self.assert_parse_equal(r'"\u0022"', StringAst, "\u0022", 0, 8)

    @given(st.text())
    @example('')
    def test_random_strings(self, s):
        print(s, repr(s))
        to_parse = f'"{repr(s)[1:-1].replace('"', r'\"')}"'
        self.assert_parse_equal(to_parse, StringAst, s, 0, len(to_parse))


    #TODO: test unicode pairs, etc