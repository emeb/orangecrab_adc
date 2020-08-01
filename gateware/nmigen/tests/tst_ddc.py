# tst_tuner.py - testbench for tuner.py
# 2020-07-30 E. Brombaugh

from nmigen.sim.pysim import *
from ddc import *

if __name__ == "__main__":
    dut = ddc()
    sim = Simulator(dut)
    Fsamp = 40e6
    Fsig = 1.445e6
    omega = 2*math.pi*Fsig/Fsamp
    Flo = 1.44e6
    phsinc = int(2**26 * Flo / Fsamp)
    with sim.write_vcd("ddc.vcd"):
        def proc():
            yield dut.frequency.eq(phsinc) # 1.44MHz
            yield dut.rate.eq(3)
            yield dut.shift.eq(7)
            for i in range( 65536 ):
                yield dut.input.eq(int(math.floor(math.sin(i*omega)*511 + 0.5)))
                yield Tick()
        sim.add_clock( 1/Fsamp )
        sim.add_sync_process( proc )
        sim.run()
