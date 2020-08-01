# pdm_dac.py - pulse-density modulation DAC
# 2020-08-01 E. Brombaugh
# based on dac.DeltaSigma from Joshua Koike/TiltmeSenpai

from nmigen import *

class pdm_dac(Elaboratable):
    def __init__(self, isz = 16):
        # Ports
        self.in_port  = Signal(signed(isz))
        self.out_port = Signal()
    
    def elaborate(self, platform):
        m = Module()
        
        ob = Signal(self.in_port.width)
        accumulator = Signal(self.in_port.width + 1)
        
        m.d.sync += [
            ob.eq(self.in_port + 2**(self.in_port.width-1)),
            self.out_port.eq(accumulator[-1]),
            accumulator.eq(accumulator[:-1] + ob)
        ]

        return m