from typing import Any
import re
import textwrap
import pytest
from typer.testing import CliRunner
from spy.__main__ import app


# https://stackoverflow.com/a/14693789
# 7-bit C1 ANSI sequences
ANSI_ESCAPE = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)

def decolorize(s: str) -> str:
    return ANSI_ESCAPE.sub('', s)


@pytest.mark.usefixtures('init')
class TestMain:
    tmpdir: Any

    @pytest.fixture
    def init(self, tmpdir):
        self.tmpdir = tmpdir
        self.runner = CliRunner()
        self.foo_spy = tmpdir.join('foo.spy')
        self.foo_spy.write(textwrap.dedent("""
        def add(x: i32, y: i32) -> i32:
            return x + y
        """))

    def run(self, *args: Any) -> None:
        args = [str(arg) for arg in args]
        print('run: spy %s' % ' '.join(args))
        res = self.runner.invoke(app, args)
        print(res.stdout)
        if res.exit_code != 0:
            raise res.exception
        return res, decolorize(res.stdout)

    def test_pyparse(self):
        res, stdout = self.run('--pyparse', self.foo_spy)
        assert stdout.startswith('py:Module(')

    def test_parse(self):
        res, stdout = self.run('--parse', self.foo_spy)
        assert stdout.startswith('Module(')
