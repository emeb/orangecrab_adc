# cic.py - quadrature CIC filter
# 2020-07-31 E. Brombaugh

from nmigen import *
from cic_slice import *

class cic(Elaboratable):
    def __init__(self, nStages = 4, gsz = 8, isz = 10):
        # save params
        self.nStages = nStages          # number of stages
        self.gsz = gsz                  # bit growth per stage
        self.isz = isz                  # input word size
        self.osz = isz + nStages * gsz  # output word size
        
        # ports
        self.input_i = Signal(signed(isz))
        self.input_q = Signal(signed(isz))
        self.rate = Signal(2)
        self.out_i = Signal(signed(self.osz))
        self.out_q = Signal(signed(self.osz))
        self.valid = Signal()

    def elaborate(self, platform):
        m = Module()
        
        m.submodules.i_slice = cic_slice(nStages = self.nStages, gsz = self.gsz, isz = self.isz)
        m.submodules.q_slice = cic_slice(nStages = self.nStages, gsz = self.gsz, isz = self.isz)
        
        # decimation rate generator
        drate = Signal(self.gsz)
        m.d.sync += drate.eq(255>>self.rate)
        dcnt = Signal(self.gsz)
        ena_cic = Signal()
        with m.If(dcnt == 0):
            m.d.sync += dcnt.eq(drate)
            m.d.sync += ena_cic.eq(1)
        with m.Else():
            m.d.sync += dcnt.eq(dcnt - 1)
            m.d.sync += ena_cic.eq(0)
        
        # hook up slices
        m.d.comb += [
            m.submodules.i_slice.input.eq(self.input_i),
            m.submodules.q_slice.input.eq(self.input_q),
            m.submodules.i_slice.ena_out.eq(ena_cic),
            m.submodules.q_slice.ena_out.eq(ena_cic),
            self.out_i.eq(m.submodules.i_slice.output),
            self.out_q.eq(m.submodules.q_slice.output),
            self.valid.eq(m.submodules.i_slice.valid)
        ]
        
        return m
