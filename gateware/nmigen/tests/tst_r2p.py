# tst_r2p.py - testbench for Rect -> Polar converter
# 2020-08-02 E. Brombaugh

import math as math
from nmigen.sim.pysim import *
from r2p import *

if __name__ == "__main__":
    dut = r2p()
    sim = Simulator(dut)
    frq = 2*math.pi/256
    with sim.write_vcd("r2p.vcd"):
        def proc():
            k = 0
            for i in range( 10000 ):
                if(i%32==0):
                    yield dut.input_x.eq(int(math.floor(math.cos(k*frq)*32767 + 0.5)))
                    yield dut.input_y.eq(int(math.floor(-math.cos(k*frq)*32767 + 0.5)))
                    k = k + 1
                    yield dut.ena.eq(1)
                else:
                    yield dut.ena.eq(0)
                    
                yield Tick()
        sim.add_clock( 1/40e6 )
        sim.add_sync_process( proc )
        sim.run()
