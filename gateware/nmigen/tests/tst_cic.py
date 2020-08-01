# tst_cic.py - testbench for I/Q CIC.py
# 2020-07-31 E. Brombaugh

import math as math
from nmigen.sim.pysim import *
from cic import *

if __name__ == "__main__":
    dut = cic()
    sim = Simulator(dut)
    frq = 2*math.pi/2048
    with sim.write_vcd("cic.vcd"):
        def proc():
            yield dut.rate.eq(3)
            for i in range( 10000 ):
                yield dut.input_i.eq(int(math.floor(math.cos(i*frq)*511 + 0.5)))
                yield dut.input_q.eq(int(math.floor(math.sin(i*frq)*511 + 0.5)))
                yield Tick()
        sim.add_clock( 1e-6 )
        sim.add_sync_process( proc )
        sim.run()
