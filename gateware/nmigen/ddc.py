# ddc.py - IF quadrature decimating downconverter
# 2020-07-31 E. Brombaugh

from nmigen import *

from tuner import *
from cic import *
from gainshift import *
from fir8dec import *

class ddc(Elaboratable):
    def __init__(self, dsz = 10, fsz = 26, osz = 16):
        # save params
        self.dsz = dsz
        self.fsz = fsz
        self.osz = osz
        
        # ports
        self.input = Signal(signed(dsz))
        self.frequency = Signal(signed(fsz))
        self.rate = Signal(2)
        self.shift = Signal(3)
        self.out_i = Signal(signed(osz))
        self.out_q = Signal(signed(osz))
        self.valid = Signal()
        self.sathld = Signal(8)
        
    def elaborate(self, platform):
        m = Module()
        
        # declare functional blocks
        m.submodules.tuner = tuner(dsz = self.dsz, fsz = self.fsz)
        m.submodules.cic = cic(nStages = 4, gsz = 8, isz = self.dsz)
        m.submodules.gainshift = gainshift(isz = m.submodules.cic.out_i.width, osz = self.osz)
        m.submodules.fir8dec = fir8dec(isz = self.osz, osz = self.osz)
        
        # hook up functional blocks
        m.d.comb += [
            m.submodules.tuner.input.eq(self.input),
            m.submodules.tuner.frequency.eq(self.frequency),
            m.submodules.cic.input_i.eq(m.submodules.tuner.out_i),
            m.submodules.cic.input_q.eq(m.submodules.tuner.out_q),
            m.submodules.cic.rate.eq(self.rate),
            m.submodules.gainshift.input_i.eq(m.submodules.cic.out_i),
            m.submodules.gainshift.input_q.eq(m.submodules.cic.out_q),
            m.submodules.gainshift.ena.eq(m.submodules.cic.valid),
            m.submodules.gainshift.shift.eq(self.shift),
            m.submodules.fir8dec.input_i.eq(m.submodules.gainshift.output_i),
            m.submodules.fir8dec.input_q.eq(m.submodules.gainshift.output_q),
            m.submodules.fir8dec.ena.eq(m.submodules.gainshift.valid),
            self.out_i.eq(m.submodules.fir8dec.output_i),
            self.out_q.eq(m.submodules.fir8dec.output_q),
            self.valid.eq(m.submodules.fir8dec.valid),
            self.sathld.eq(m.submodules.gainshift.sathld)
        ]
        
        return m
