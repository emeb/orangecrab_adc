# r2p.py - CORDIC Rectangular to Polar converter
# 2020-08-02 E. Brombaugh

from nmigen import *
import math as math
import numpy as np

class r2p(Elaboratable):
    def __init__(self, dsz = 16, psz = 16):
        # save params
        self.dsz = dsz
        self.psz = psz
        self.iterations = 16
        self.gsz = 4
        
        # constants
        pscl = (2**(psz-1))-1
        itr = range(self.iterations)
        phi = [int(math.atan(2**-i)/math.pi * 2**(psz-1) + 0.5) for i in itr]
        k = 1
        for i in itr:
            k = k*math.sqrt(1 + 2**(-2*i))
        self.k = int(2**dsz/k)
        
        #print(data)
        #print(self.k)
                
        # array for phi values
        self.LUT = Array([Signal(unsigned(psz)) for _ in range(self.iterations)])        
        for i in itr:
            self.LUT[i] = phi[i]
        
        # ports
        self.input_x = Signal(signed(dsz))
        self.input_y = Signal(signed(dsz))
        self.ena = Signal()
        self.mag = Signal(unsigned(dsz))
        self.angle = Signal(signed(psz))
        self.valid = Signal()
        
    def elaborate(self, platform):
        m = Module()
        
        # initial values - handle x<0
        xi = Signal(signed(self.input_x.width))
        yi = Signal(signed(self.input_y.width))
        ai = Signal(signed(self.angle.width))
        with m.If(self.ena):
            m.d.sync += [
                xi.eq(Mux(self.input_x[-1], -self.input_x, self.input_x)),
                yi.eq(Mux(self.input_x[-1], -self.input_y, self.input_y)),
                ai.eq(Mux(self.input_x[-1], Cat(Repl(0,self.angle.width-1),1), 0))
            ]
        
        # delay enable
        ena_d1 = Signal()
        m.d.sync += ena_d1.eq(self.ena)
        
        # iteration state machine
        itr = Signal(range(self.iterations))
        run = Signal()
        done = Signal()
        with m.FSM():
            with m.State('WAIT'):
                m.d.sync += done.eq(0)
                with m.If(ena_d1):
                    m.next = 'RUN'
                    m.d.sync += [
                        itr.eq(0),
                        run.eq(1)
                    ]
                    
            with m.State('RUN'):
                with m.If(itr == (self.iterations-1)):
                    m.next = 'WAIT'
                    m.d.sync += [
                        run.eq(0),
                        done.eq(1)
                    ]
                with m.Else():
                    m.d.sync += itr.eq(itr+1)
        
        # delay controls
        run_d1 = Signal()
        itr_d1 = Signal(itr.width)
        m.d.sync += [
            run_d1.eq(run),
            itr_d1.eq(itr)
        ]
        
        # phase LUT
        phi = Signal(signed(self.psz))
        m.d.sync += phi.eq(self.LUT[itr])
            
        # iteration accumulators
        xacc = Signal(signed(self.dsz+self.gsz+2))
        yacc = Signal(signed(self.dsz+self.gsz+1))
        aacc = Signal(signed(self.psz))
        sx = Signal(signed(self.dsz+self.gsz+2))
        sy = Signal(signed(self.dsz+self.gsz+1))
        m.d.comb += [
            sx.eq(xacc>>itr_d1),
            sy.eq(yacc>>itr_d1)
        ]
        with m.If(run & ~run_d1):
            m.d.sync += [
                xacc.eq(xi<<self.gsz),
                yacc.eq(yi<<self.gsz),
                aacc.eq(ai)
            ]
        with m.Elif(run_d1):
            with m.If(yacc[-1]):
                m.d.sync += [
                    xacc.eq(xacc - sy),
                    yacc.eq(yacc + sx),
                    aacc.eq(aacc - phi)
                ]
            with m.Else():
                m.d.sync += [
                    xacc.eq(xacc + sy),
                    yacc.eq(yacc - sx),
                    aacc.eq(aacc + phi)
                ]
        
        # scale and hold output
        done = Signal(2)
        mscale = Signal(2*self.dsz+1)
        m.d.sync += [
            done.eq(Cat(~run & run_d1, done[0])),
            self.valid.eq(done[1])
        ]
        uxacc = Signal(unsigned(self.dsz+1))
        m.d.comb += uxacc.eq(xacc>>self.gsz)
        with m.If(done[0]):
            m.d.sync += mscale.eq(uxacc*self.k)
        with m.If(done[1]):
            m.d.sync += [
                self.angle.eq(aacc),
                self.mag.eq(mscale>>self.dsz)
            ]
        
        return m