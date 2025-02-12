# tests = [
#     ("1/2", (Rational(PosOrNeg.POS, DecimalInt(1), DecimalInt(2)), 0, 3)),
#     ("-1/2", (Rational(PosOrNeg.NEG, DecimalInt(1), DecimalInt(2)), 0, 4)),
#     ("-100/101", (Rational(PosOrNeg.NEG, DecimalInt(100), DecimalInt(101)), 0, 8)),
#     ("#e#b1100/1101", (Rational(PosOrNeg.POS, BinaryInt(12), BinaryInt(13)), 0, 13)),
#     ("#o#e-27", (Rational(PosOrNeg.NEG, OctalInt(23), OctalInt(1)), 0, 7)),
#     ("#xFFFF", (Rational(PosOrNeg.POS, HexInt(65535), HexInt(1)), 0, 6)),
#     ("#x-F0/23", (Rational(PosOrNeg.NEG, HexInt(240), HexInt(35)), 0, 8)),
#     ("#d#e100.0010", (Rational(PosOrNeg.POS, DecimalInt(1000010), DecimalInt(10000)), 0, 12)),
# ]
# for (test, (value, start, end)) in tests:
#     result = p.parse_ast(test)
#     assert isinstance(result, NumberAst)
#     assert result == value
#     assert result.meta.start_pos == start
#     assert result.meta.end_pos == end
#
# def test_exact_complex():
#     p = PyracketParser(start="number", propagate_positions=True)
#     tests = [
#         ("+i", (Complex(Rational.make(0, 1), Rational.make(1, 1)), 0, 2)),
#     ]
#     for (test, (value, start, end)) in tests:
#         result = p.parse_ast(test)
#         assert isinstance(result, NumberAst)
#         assert result == value
#         assert result.meta.start_pos == start
#         assert result.meta.end_pos == end