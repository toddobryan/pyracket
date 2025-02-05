from lark.tree import Meta
from pyracket.pyracket_ast import *


#TODO: Figure out how to test negative examples

def test_boolean():
    p = PyracketParser(start="boolean", propagate_positions=True)
    tests = [
        ("#true", (True, 0, 5)),
        ("#false", (False, 0, 6)),
    ]
    for (test, (value, start, end)) in tests:
        result = p.parse_ast(test)
        assert isinstance(result, Boolean)
        assert result.value == value
        assert result.meta.start_pos == start
        assert result.meta.end_pos == end

def test_string():
    p = PyracketParser(start="string", propagate_positions=True)
    tests = [
        ('"hello"', ("hello", 0, 7)),
        ('"hello world"', ("hello world", 0, 13)),
        ('"hello world!"', ("hello world!", 0, 14)),
        ('""', ('', 0, 2)),
        (r'"\t"', ('\t', 0, 4)),
        (r'"\""', ('"', 0, 4)),
        (r'"\40"', (" ", 0, 5)),
        (r'"\u0022"', ("\u0022", 0, 8)),
    ]
    for (test, (value, start, end)) in tests:
         result = p.parse_ast(test)
         assert isinstance(result, String)
         assert result.value == value
         assert result.meta.start_pos == start
         assert result.meta.end_pos == end
         
def test_unsigned_rationals():
    p = PyracketParser(start="unsigned_rational_2", propagate_positions=True)
    tests = [
        ("101", (UnsignedRational2(BinaryInt(5), None), 0, 3)),
        ("1010/101", (UnsignedRational2(BinaryInt(10), BinaryInt(5)), 0, 8))
    ]
    for (test, (value, start, end)) in tests:
        result = p.parse_ast(test)
        assert result == value
        assert result.meta.start_pos == start
        assert result.meta.end_pos == end

def test_number():
    p = PyracketParser(start="number", propagate_positions=True)
    tests = [
        ("0", (ExactRational(UnsignedRational10(DecimalInt(0), DecimalInt(1))), 0, 1)),
        ("1/2", (ExactRational(UnsignedRational10(DecimalInt(1), DecimalInt(2))), 0, 3)),
    ]
    for (test, (value, start, end)) in tests:
        result = p.parse_ast(test)
        assert isinstance(result, Number)
        assert result.value == value
        assert result.meta.start_pos == start
        assert result.meta.end_pos == end