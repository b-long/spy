from typing import Optional
import subprocess
import py
from py.path import LocalPath
import spy

INCLUDE = spy.ROOT.join('libspy', 'include')
LIBSPY_A = spy.ROOT.join('libspy', 'libspy.a')

class ZigToolchain:

    def __init__(self) -> None:
        import ziglang  # type: ignore
        self.ZIG = py.path.local(ziglang.__file__).dirpath('zig')
        if not self.ZIG.check(exists=True):
            raise ValueError('Cannot find the zig executable; try pip install ziglang')

    def c2wasm(self, file_c: LocalPath, file_wasm: LocalPath,
               *, exports: Optional[list[str]] = None) -> LocalPath:
        """
        Compile the C code to WASM, using zig cc
        """
        cmdline = [
            str(self.ZIG), 'cc',
	    '--target=wasm32-freestanding',
	    '-nostdlib',
            '-shared',
	    '-g',
	    '-O3',
	    '-o', str(file_wasm),
	    str(file_c)
        ]
        if exports:
            for name in exports:
                cmdline.append(f'-Wl,--export={name}')
        #
        # these are needed for libspy
        cmdline += [
            '-I', str(INCLUDE),
            str(LIBSPY_A),
        ]
        subprocess.check_call(cmdline)
        return file_wasm