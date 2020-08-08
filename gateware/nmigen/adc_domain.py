# adc_domain.py - all the logic running off the ADC clock
# 2020-08-07 E. Brombaugh

from nmigen import *
from ddc import *
from demods import *
from pdm_dac import *

class adc_domain(Elaboratable):
    def __init__(self, dsz = 10):
        # save params
        self.dsz = dsz
        
        # ports
        self.adc_data = Signal(signed(dsz))
        self.pdm_l = Signal()
        self.pdm_r = Signal()
        self.clkstat = Signal()
        
    def elaborate(self, platform):
        m = Module()
        
        # instantiate the lower level blocks
        m.submodules.ddc = ddc()
        m.submodules.demods = demods()
        m.submodules.dac_l = pdm_dac()
        m.submodules.dac_r = pdm_dac()
                
        # hook up blocks
        m.d.comb += [
            # DDC
            m.submodules.ddc.input.eq(self.adc_data),
            m.submodules.ddc.frequency.eq(2415919),     # 1.440MHz
            m.submodules.ddc.rate.eq(0),
            m.submodules.ddc.shift.eq(0),
            
            # Demodulator
            m.submodules.demods.input_i.eq(m.submodules.ddc.out_i),
            m.submodules.demods.input_q.eq(m.submodules.ddc.out_q),
            m.submodules.demods.type.eq(DemodType.AM),
            m.submodules.demods.ena.eq(m.submodules.ddc.valid),
            
            # DACs
            m.submodules.dac_l.in_port.eq(m.submodules.demods.out_l),
            m.submodules.dac_r.in_port.eq(m.submodules.demods.out_r),
            self.pdm_l.eq(m.submodules.dac_l.out_port),
            self.pdm_r.eq(m.submodules.dac_r.out_port),
        ]
        
        # Clock status divider
        clk_div = Signal(23)
        m.d.sync += clk_div.eq(clk_div + 1)
        m.d.comb += self.clkstat.eq(clk_div[-1])
        
        return m
