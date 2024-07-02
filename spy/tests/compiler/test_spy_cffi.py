#-*- encoding: utf-8 -*-

import struct
import pytest
from spy.vm.b import B
from spy.vm.modules.spy_cffi import CFFI
from spy.tests.support import (CompilerTest, skip_backends, no_backend, no_C,
                               only_interp)

class TestSPyCFFI(CompilerTest):

    @only_interp
    def test_field(self):
        mod = self.compile(
        """
        from spy_cffi import Field

        def foo() -> Field:
            return Field('x', 8, i32, None, None)
        """)
        w_f = mod.foo()
        assert self.vm.unwrap(w_f.w_name) == 'x'
        assert self.vm.unwrap(w_f.w_offset) == 8
        assert w_f.w_type is B.w_i32

    @only_interp
    def test_StructType(self):
        mod = self.compile(
        """
        from spy_cffi import new_StructType, Field

        def make_Point() -> type:
            return new_StructType('Point', [
                Field('x', 0, i32, None, None),
                Field('y', 4, i32, None, None),
            ])

        Point = make_Point()
        """)
        w_Point = mod.w_mod.getattr('Point')
        assert repr(w_Point) == "<spy type 'Point' (typedef of 'RawBuffer')>"

    def test_StructObject(self):
        mod = self.compile(
        """
        from rawbuffer import rb_get_i32, RawBuffer, rb_set_i32
        from spy_cffi import new_StructType, Field

        @blue
        def Field_GET(self: Field):
            T = self.type
            def opimpl_get(obj: RawBuffer, attr: str) -> T:
                return rb_get_i32(obj, self.offset)
            return opimpl_get

        @blue
        def Field_SET(self: Field):
            T = self.type
            def opimpl_set(obj: RawBuffer, attr: str, val: T) -> void:
                rb_set_i32(obj, self.offset, val)
            return opimpl_set


        @blue
        def newField(name, offset, T) -> Field:
            return Field(name, offset, T, Field_GET, Field_SET)

        @blue
        def make_Point() -> type:
            return new_StructType('Point', [
                newField('x', 0, i32),
                newField('y', 4, i32),
            ])

        Point = make_Point()

        def setter() -> Point:
            p: Point = Point()
            p.x = 0xDDCCBBAA
            p.y = 0x44332211
            return p

        def getter() -> i32:
            p: Point = Point()
            p.x = 30
            p.y = 12
            return p.x + p.y
        """)
        buf = mod.setter()
        assert buf == bytearray(b'\xAA\xBB\xCC\xDD\x11\x22\x33\x44')
        assert mod.getter() == 42