# tuner.py - IF quadrature tuner
# 2020-07-30 E. Brombaugh

from nmigen import *

from tuner_slice import *

class tuner(Elaboratable):
    def __init__(self, dsz = 10, fsz = 26):
        # save params
        self.dsz = dsz
        self.fsz = fsz
        
        # ports
        self.input = Signal(signed(dsz))
        self.frequency = Signal(signed(fsz))
        self.out_i = Signal(signed(dsz))
        self.out_q = Signal(signed(dsz))

    def elaborate(self, platform):
        m = Module()
        
        m.submodules.i_slice = tuner_slice(dsz = self.dsz, qshf = 1)
        m.submodules.q_slice = tuner_slice(dsz = self.dsz, qshf = 0)
        psz = m.submodules.i_slice.psz
        
        # phase accumulator
        acc = Signal(signed(self.fsz))
        m.d.sync += acc.eq(acc + self.frequency)

        # hook up slices
        m.d.comb += [
            m.submodules.i_slice.input.eq(self.input),
            m.submodules.q_slice.input.eq(self.input),
            m.submodules.i_slice.phase.eq(acc[self.fsz-psz:]),
            m.submodules.q_slice.phase.eq(acc[self.fsz-psz:]),
            self.out_i.eq(m.submodules.i_slice.output),
            self.out_q.eq(m.submodules.q_slice.output)
        ]
        
        return m
