# tst_fir8dec.py - testbench for I/Q 8x decimating FIR filter
# 2020-07-31 E. Brombaugh

import math as math
from nmigen.sim.pysim import *
from fir8dec import *

if __name__ == "__main__":
    dut = fir8dec()
    sim = Simulator(dut)
    frq = 2*math.pi/90
    with sim.write_vcd("fir8dec.vcd"):
        def proc():
            k = 0
            for i in range( 20000 ):
                if(i%32==0):
                    yield dut.input_i.eq(int(math.floor(math.cos(k*frq)*32767 + 0.5)))
                    yield dut.input_q.eq(int(math.floor(math.sin(k*frq)*32767 + 0.5)))
                    k = k + 1
                    yield dut.ena.eq(1)
                else:
                    yield dut.ena.eq(0)
                    
                yield Tick()
        sim.add_clock( 1/40e6 )
        sim.add_sync_process( proc )
        sim.run()
