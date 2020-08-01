# fir8dec_slice.py - MAC slice for FIR decimate by 8
# 2020-07-31 E. Brombaugh

from nmigen import *
from sat import *

class fir8dec_slice(Elaboratable):
    def __init__(self, isz = 16, csz = 16, osz = 16, agrw = 3):
        # parameters
        self.isz = isz
        self.csz = csz
        self.osz = osz
        self.agrw = agrw
        
        # ports
        self.input = Signal(signed(isz))
        self.coeff = Signal(signed(csz))
        self.mac_ena = Signal()
        self.dump = Signal()
        self.output = Signal(signed(osz))
        
    def elaborate(self, platform):
        m = Module()
        
        # multiplier
        mult = Signal(signed(self.csz+self.isz))
        m.d.sync += mult.eq(self.input * self.coeff)

        # accumulator
        acc = Signal(signed(self.csz+self.isz+self.agrw))
        rnd_const = Const(1<<(self.csz+1), signed(self.csz+self.isz+self.agrw))
        with m.If(self.mac_ena):
            m.d.sync += acc.eq(acc + mult)
        with m.Else():
            m.d.sync += acc.eq(rnd_const)
        
        # truncate, saturate and hold output
        m.submodules.sat = sat(isz = self.agrw+self.osz-2, osz = self.osz)
        m.d.comb += m.submodules.sat.input.eq(acc[self.csz+2:])
        with m.If(self.dump):
            m.d.sync += self.output.eq(m.submodules.sat.output)
            
        return m