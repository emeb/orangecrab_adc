# dcb.py - simple DC blocking
# 2020-08-05 E. Brombaugh

from nmigen import *
from sat import *

class dcb(Elaboratable):
    def __init__(self, dsz = 16, dc_coeff = 10):
        # params
        self.dsz = dsz
        self.dc_coeff = dc_coeff
        
        # ports
        self.input = Signal(signed(dsz))
        self.ena = Signal()
        self.output = Signal(signed(dsz))
        self.valid = Signal()
        
    def elaborate(self, platform):
        m = Module()
        
        # accumulate DC and subtract
        dcb_acc = Signal(signed(self.dsz + 1 + self.dc_coeff))
        dcb_out = Signal(signed(self.dsz + 1))
        valid_pipe = Signal(2)
        m.d.sync += valid_pipe.eq(Cat(self.ena, valid_pipe[0]))
        with m.If(self.ena):
            m.d.sync += [
                dcb_acc.eq(dcb_acc + dcb_out),
                dcb_out.eq(self.input - (dcb_acc>>self.dc_coeff))
            ]
            
        # saturate DC block output
        m.submodules.dcb_sat = sat(isz=self.dsz+1, osz = self.dsz)
        m.d.comb += m.submodules.dcb_sat.input.eq(dcb_out)
        with m.If(valid_pipe[0]):
             m.d.sync += self.output.eq(m.submodules.dcb_sat.output)
        m.d.comb += self.valid.eq(valid_pipe[1])
        
        return m        
