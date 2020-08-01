# tst_tuner_slice.py - testbench for tuner_slice.py
# 2020-07-30 E. Brombaugh

from nmigen.sim.pysim import *
from tuner_slice import *

if __name__ == "__main__":
    dut = tuner_slice(qshf = 0)
    sim = Simulator(dut)
    with sim.write_vcd("tuner_slice.vcd"):
        def proc():
            yield dut.input.eq(-512)
            for i in range( 10000 ):
                yield dut.phase.eq(dut.phase + 1)
                yield Tick()
        sim.add_clock( 1e-6 )
        sim.add_sync_process( proc )
        sim.run()
