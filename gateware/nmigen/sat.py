# sat.py - basic signed saturation
# 2020-07-31 E. Brombaugh

from nmigen import *
import operator

class sat(Elaboratable):
    def __init__(self, isz = 17, osz = 12):
        # params
        self.isz = isz
        self.osz = osz
        
        # ports
        self.input = Signal(signed(isz))
        self.output = Signal(signed(osz))
        self.flag = Signal()
        
    def elaborate(self, platform):
        m = Module()

        # min and max detection
        min = Signal()
        max = Signal()
        m.d.comb += [
            min.eq(self.input[-1] & ~self.input[self.osz-1:self.isz-1].all()),
            max.eq(~self.input[-1] & self.input[self.osz-1:self.isz-1].any()),
            self.flag.eq(min|max)
        ]
        
        # mux outputs
        with m.Switch(Cat(min,max)):
            with m.Case(1):
                # max neg
                m.d.comb += self.output.eq(Cat(Repl(0,self.osz-1),1)) 
            with m.Case(2):
                # max pos
                m.d.comb += self.output.eq(Cat(Repl(1,self.osz-1),0))
            with m.Default():
                # pass thru
                m.d.comb += self.output.eq(self.input)
        
        return m        
