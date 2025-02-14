from importlib import resources as impres
from typing import TypeVar
from lark import Lark, ast_utils
from lark.ast_utils import Ast
from lark.tree import Meta

from pyracket.syntax.expr_ast import ToAstExpr

T = TypeVar("T")

expr_transformer = ToAstExpr()

class PyracketParser(Lark):
    def __init__(
            self, **options
    ) -> None:
        super().__init__(
            read_expr_grammar(), propagate_positions=True, **options)

    def parse_ast(self, text: str) -> Ast:
        return expr_transformer.transform(self.parse(text))

def read_expr_grammar() -> str:
    return (impres.files(__package__) / "expr.lark").read_text()
