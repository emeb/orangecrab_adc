# gainshift.py - post-CIC gain adjustment
# 2020-08-01 E. Brombaugh

from nmigen import *
from sat import *

class gainshift(Elaboratable):
    def __init__(self, isz = 42, ssz = 3, osz = 16):
        # save params
        self.isz = isz
        self.ssz = ssz
        self.osz = osz
        
        # ports
        self.input_i = Signal(signed(isz))
        self.input_q = Signal(signed(isz))
        self.ena = Signal()
        self.shift = Signal(ssz)
        self.output_i = Signal(signed(osz))
        self.output_q = Signal(signed(osz))
        self.valid = Signal()
        self.sathld = Signal(8)
        
    def elaborate(self, platform):
        m = Module()
        
        # pipe the enable
        ena_pipe = Signal(2)
        m.d.sync += ena_pipe.eq(Cat(self.ena,ena_pipe[0]))
        m.d.comb += self.valid.eq(ena_pipe[1])
        
        # shift inputs up
        shf_i = Signal(signed(self.isz+7))
        shf_q = Signal(signed(self.isz+7))
        m.d.sync += [
            shf_i.eq(self.input_i<<self.shift),
            shf_q.eq(self.input_q<<self.shift)
        ]
        
        # truncate and saturate to output 
        m.submodules.sat_i = sat(isz = self.osz+7, osz = self.osz)
        m.submodules.sat_q = sat(isz = self.osz+7, osz = self.osz)
        m.d.comb += [
            m.submodules.sat_i.input.eq(shf_i[self.isz-self.osz:]),
            m.submodules.sat_q.input.eq(shf_q[self.isz-self.osz:])
        ]
        m.d.sync += [
            self.output_i.eq(m.submodules.sat_i.output),
            self.output_q.eq(m.submodules.sat_q.output)
        ]
        
        # count up saturation events
        satval = Signal(8)
        satcnt = Signal(8)
        with m.If(ena_pipe[0]):
            m.d.sync += satcnt.eq(satcnt+1)
            with m.If(satcnt==0):
                m.d.sync += [
                    satval.eq(m.submodules.sat_i.flag | m.submodules.sat_i.flag),
                    self.sathld.eq(satval)
                ]
            with m.Else():
                m.d.sync += [
                    satval.eq(satval + (m.submodules.sat_i.flag | m.submodules.sat_i.flag))
                ]
        
        return m
    