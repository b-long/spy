from typing import Any, Literal, Optional
import textwrap
import pytest
from spy.vm.vm import SPyVM
from spy.backend.interp import InterpModuleWrapper

@pytest.mark.usefixtures('init')
class TestBlueMod:

    @pytest.fixture
    def init(self, tmpdir):
        self.tmpdir = tmpdir
        self.vm = SPyVM()
        self.vm.path.append(str(tmpdir))

    def write_file(self, filename: str, src: str) -> Any:
        """
        Write the give source code to the specified filename, in the tmpdir.

        The source code is automatically dedented.
        """
        src = textwrap.dedent(src)
        srcfile = self.tmpdir.join(filename)
        srcfile.write(src)
        return srcfile

    def import_(self, src: str) -> Any:
        self.write_file("test.spy", src)
        w_mod = self.vm.import_("test")
        return InterpModuleWrapper(self.vm, w_mod)

    def test_simple(self):
        mod = self.import_("""
        @blue
        def foo():
            return 42
        """)
        assert mod.foo() == 42

    def test_param(self):
        mod = self.import_("""
        @blue
        def foo(x):
            return x
        """)
        assert mod.foo(53) == 53
