# tst_r2p.py - testbench for Rect -> Polar converter
# 2020-08-02 E. Brombaugh

import math as math
from nmigen.sim.pysim import *
from demods import *

if __name__ == "__main__":
    dut = demods()
    sim = Simulator(dut)
    frqc = 2*math.pi/100
    frqm = 2*math.pi/32
    with sim.write_vcd("demods.vcd"):
        def proc():
            k = 0
            yield(dut.type.eq(DemodType.AM))
            for i in range( 50000 ):
                if(i%32==0):
                    if 1:
                        # AM
                        m = math.cos(k*frqm)/2 + 0.5
                        yield dut.input_i.eq(int(m*math.floor(math.cos(k*frqc)*32767 + 0.5)))
                        yield dut.input_q.eq(int(m*math.floor(math.sin(k*frqc)*32767 + 0.5)))
                    else:
                        # FM
                        m = math.cos(k*frqm)/10
                        yield dut.input_i.eq(int(math.floor(math.cos(k*frqc+m)*32767 + 0.5)))
                        yield dut.input_q.eq(int(math.floor(math.sin(k*frqc+m)*32767 + 0.5)))
                        
                    k = k + 1
                    yield dut.ena.eq(1)
                else:
                    yield dut.ena.eq(0)
                    
                yield Tick()
        sim.add_clock( 1/40e6 )
        sim.add_sync_process( proc )
        sim.run()
