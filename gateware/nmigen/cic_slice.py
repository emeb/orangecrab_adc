# cic_slice.py - CIC decimator logic. needs external rate enable
# 2020-07-31 E. Brombaugh

from nmigen import *
import math as math
import numpy as np

class cic_slice(Elaboratable):
    def __init__(self, nStages = 4, gsz = 8, isz = 10):
        # save params
        self.nStages = nStages          # number of stages
        self.gsz = gsz                  # bit growth per stage
        self.isz = isz                  # input word size
        self.asz = isz + nStages * gsz  # Integrator/Adder word size
        self.osz = self.asz	            # Output word size
        
        # ports
        self.input = Signal(signed(self.isz))
        self.ena_out = Signal()
        self.output = Signal(signed(self.osz))
        self.valid = Signal()
        
    def elaborate(self, platform):
        m = Module()
        
        # integrators
        integrator = Array([Signal(signed(self.asz)) for _ in range(self.nStages)])        
        for i in range(self.nStages):
            if(i==0):
                m.d.sync += integrator[i].eq(integrator[i] + self.input)
            else:
                m.d.sync += integrator[i].eq(integrator[i] + integrator[i-1])
        integrator_out = Signal(signed(self.asz))
        m.d.comb += integrator_out.eq(integrator[-1])
            
        # decimation and combs
        comb_pipe = Signal(self.nStages+1)
        m.d.sync += comb_pipe.eq(Cat(self.ena_out, comb_pipe[:(self.nStages+1)]))
        comb_ena = Signal(self.nStages+2)
        m.d.comb += comb_ena.eq(Cat(self.ena_out, comb_pipe))
        comb_diff = Array([Signal(signed(self.osz)) for _ in range(self.nStages+1)])
        comb_dly = Array([Signal(signed(self.osz)) for _ in range(self.nStages+1)])
        for i in range(self.nStages+1):
            with m.If(comb_ena[i]):
                if(i==0):
                    m.d.sync += comb_diff[i].eq(integrator_out>>(self.asz-self.osz))
                else:
                    m.d.sync += comb_diff[i].eq(comb_diff[i-1] - comb_dly[i-1])
                m.d.sync += comb_dly[i].eq(comb_diff[i])
        
        # hook up outputs
        m.d.sync += self.output.eq(comb_diff[-1])
        m.d.sync += self.valid.eq(comb_ena[-1])
        
        return m