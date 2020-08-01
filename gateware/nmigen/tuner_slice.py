# tuner_slice.py - one arm of a quadrature tuner. Includes sin/cos LUT and
# mixer logic
# 2020-07-30 E. Brombaugh

from nmigen import *
import math as math
import numpy as np

class tuner_slice(Elaboratable):
    def __init__(self, dsz = 10, psz = 12, qshf = 0):
        # save params
        self.dsz = dsz
        self.psz = psz
        self.qshf = qshf
        
        # define the LUT contents
        sine_len = 2**(psz-2)
        scl = (2**(dsz-1))-1
        data = np.zeros(sine_len, dtype=np.int)
        for i in np.arange(sine_len):
            data[i] = int(np.floor(np.sin((i+0.5)*np.pi/(2*sine_len))*scl + 0.5))
            
        #print(data)
        
        # create the LUT
        self.LUT = Memory(width = dsz, depth = sine_len, init = data)
    
        # LUT read port
        self.r = self.LUT.read_port(transparent=False)
        
        # ports
        self.input = Signal(signed(dsz))
        self.phase = Signal(signed(psz))
        self.output = Signal(signed(dsz))

    def elaborate(self, platform):
        m = Module()
        
        # extract address bits from phase and delay one cycle
        p_quad = Signal(2)
        m.d.comb += p_quad.eq(self.phase[-2:] + self.qshf)
        quad = Signal(2)
        m.d.sync += quad.eq(p_quad)
        addr = Signal(self.psz-2)
        m.d.sync += addr.eq(self.phase[:-2] ^ Repl(p_quad[0],self.psz-2))
        sincos_sign = Signal()
        m.d.sync += sincos_sign.eq(quad[1])
        
        # LUT with 1/4 cycle sine
        m.submodules.r = self.r
        m.d.comb += self.r.addr.eq(addr)
        sincos_raw = Signal(signed(self.dsz))
        m.d.comb += sincos_raw.eq(self.r.data)
        
        # sign inversion to get full wave
        sincos = Signal(signed(self.dsz))
        m.d.sync += sincos.eq(Mux(sincos_sign, -sincos_raw, sincos_raw))
        
        # signed multiply input by sinusoid
        product = Signal(signed(2*self.dsz))
        m.d.sync += product.eq(self.input * sincos)
        
        # round off
        prod_rnd = Signal(signed(self.dsz+1))
        m.d.sync += prod_rnd.eq((product[self.dsz-2:] + 1)//2)
        
        # saturate not needed here?
        m.d.comb += self.output.eq(prod_rnd[:-1])
        
        return m