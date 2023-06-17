import ast as py_ast
from typing import Any
import pytest
from spy.parser import Parser
from spy.errors import SPyParseError
from spy import ast

class AnythingClass:

    def __repr__(self):
        return '<ANYTHING>'

    def __eq__(self, other):
        return True

ANYTHING: Any = AnythingClass()  # type:ignore

class TestParser:

    def parse(self, src) -> ast.Module:
        p = Parser.from_string(src, dedent=True)
        return p.parse()

    def test_Module(self):
        mod = self.parse("""
        def foo() -> void:
            pass
        """)
        expected = ast.Module(
            decls = [
                ast.FuncDef(
                    loc = ANYTHING,
                    name = 'foo',
                    args = [],
                    return_type = ast.Name(loc=ANYTHING, id='void'),
                    body = ANYTHING,
                )
            ]
        )
        assert mod == expected

    def test_FuncDef_arguments(self):
        mod = self.parse("""
        def foo(a: i32, b: float) -> void:
            pass
        """)
        funcdef = mod.decls[0]
        assert isinstance(funcdef, ast.FuncDef)
        expected = ast.FuncDef(
            loc = ANYTHING,
            name = 'foo',
            args = [
                ast.FuncArg(ANYTHING, 'a', ast.Name(ANYTHING, 'i32')),
                ast.FuncArg(ANYTHING, 'b', ast.Name(ANYTHING, 'float'))
            ],
            return_type = ast.Name(loc=ANYTHING, id='void'),
            body = ANYTHING,
        )
        assert funcdef == expected


    def test_FuncDef_errors(self):
        with pytest.raises(SPyParseError, match="missing return type"):
            mod = self.parse("""
            def foo():
                pass
            """)
        #
        with pytest.raises(SPyParseError, match=r"\*args is not supported yet"):
            mod = self.parse("""
            def foo(*args) -> void:
                pass
            """)
        #
        with pytest.raises(SPyParseError, match=r"\*\*kwargs is not supported yet"):
            mod = self.parse("""
            def foo(**kwargs) -> void:
                pass
            """)
        #
        with pytest.raises(SPyParseError,
                           match="default arguments are not supported yet"):
            mod = self.parse("""
            def foo(a: i32 = 42) -> void:
                pass
            """)
        #
        with pytest.raises(SPyParseError,
                           match="positional-only arguments are not supported yet"):
            mod = self.parse("""
            def foo(a: i32, /, b: i32) -> void:
                pass
            """)
        #
        with pytest.raises(SPyParseError,
                           match="keyword-only arguments are not supported yet"):
            mod = self.parse("""
            def foo(a: i32, *, b: i32) -> void:
                pass
            """)
        #
        with pytest.raises(SPyParseError, match="missing type for argument 'a'"):
            mod = self.parse("""
            def foo(a, b) -> void:
                pass
            """)
        #
        with pytest.raises(SPyParseError, match="decorators are not supported yet"):
            mod = self.parse("""
            @mydecorator
            def foo() -> void:
                pass
            """)


    def test_FuncDef_body(self):
        mod = self.parse("""
        def foo() -> i32:
            return 42
        """)
        funcdef = mod.decls[0]
        assert isinstance(funcdef, ast.FuncDef)
        assert len(funcdef.body) == 1
        stmt = funcdef.body[0]
        assert isinstance(stmt, py_ast.Return)
