# tst_tuner.py - testbench for tuner.py
# 2020-07-30 E. Brombaugh

from nmigen.sim.pysim import *
from tuner import *

if __name__ == "__main__":
    dut = tuner()
    sim = Simulator(dut)
    with sim.write_vcd("tuner.vcd"):
        def proc():
            yield dut.input.eq(-512)
            yield dut.frequency.eq(16384)
            for i in range( 10000 ):
                yield Tick()
        sim.add_clock( 1e-6 )
        sim.add_sync_process( proc )
        sim.run()
