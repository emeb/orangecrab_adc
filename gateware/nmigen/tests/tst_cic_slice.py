# tstcic_slice.py - testbench for cic_slice.py
# 2020-07-31 E. Brombaugh

import math as math
from nmigen.sim.pysim import *
from cic_slice import *

if __name__ == "__main__":
    dut = cic_slice()
    sim = Simulator(dut)
    frq = 2*math.pi/2048
    with sim.write_vcd("cic_slice.vcd"):
        def proc():
            for i in range( 10000 ):
                yield dut.input.eq(int(math.floor(math.sin(i*frq)*511 + 0.5)))
                if(i%256==0):
                    yield dut.ena_out.eq(1)
                else:
                    yield dut.ena_out.eq(0)
                
                yield Tick()
        sim.add_clock( 1e-6 )
        sim.add_sync_process( proc )
        sim.run()
