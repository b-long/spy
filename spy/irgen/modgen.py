import ast as py_ast
import spy.ast
from spy.irgen.typechecker import TypeChecker
from spy.irgen.codegen import CodeGen
from spy.vm.vm import SPyVM
from spy.vm.module import W_Module
from spy.vm.object import W_Type
from spy.vm.function import W_FunctionType, W_Function


class ModuleGen:
    """
    Generate a W_Module, given a spy.ast.Module.
    """
    vm: SPyVM
    mod: spy.ast.Module
    t: TypeChecker

    def __init__(self, vm: SPyVM, t: TypeChecker, mod: spy.ast.Module) -> None:
        self.vm = vm
        self.t = t
        self.mod = mod

    def make_w_mod(self) -> W_Module:
        name = 'mymod' # XXX
        self.w_mod = W_Module(self.vm, name)
        for decl in self.mod.decls:
            assert isinstance(decl, spy.ast.FuncDef)
            w_func = self.make_w_func(decl)
            self.w_mod.add(w_func.w_code.name, w_func)
        return self.w_mod

    def make_w_func(self, funcdef: spy.ast.FuncDef) -> W_Function:
        w_functype, scope = self.t.get_funcdef_info(funcdef)
        codegen = CodeGen(self.vm, funcdef, w_functype)
        w_code = codegen.make_w_code()
        w_func = W_Function(w_functype, w_code, self.w_mod.content)
        return w_func