# top.py - top level of IF quadrature decimating downconverter
# 2020-08-01 E. Brombaugh

from nmigen import *
from ddc import *
from pdm_dac import *
from nmigen_boards.orangecrab_r0_2 import OrangeCrabR0_2Platform
from nmigen.build import *

class top(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        
        # declare the I/O we're using
        ad9203   = platform.request("ad9203", 0)
        usrbtn   = platform.request("button", 0)
        programn = platform.request("program", 0)
        rgb_led = platform.request("rgb_led", 0)
        pdm_out = platform.request("pdm_out", 0)
        
        # use the 40MHz ADC clock
        m.domains.sync = ClockDomain()
        clk40 = Signal()
        platform.add_clock_constraint(clk40, 40e6)
        m.d.comb += [
            clk40.eq(ad9203.clk),
            ClockSignal("sync") .eq(clk40)
        ]
        
        # internal signals
        pdm_l = Signal()
        pdm_r = Signal()
        
        # instantiate the lower level blocks
        m.submodules.ddc = ddc()
        m.submodules.dac_l = pdm_dac()
        m.submodules.dac_r = pdm_dac()
        
        # hook up blocks
        m.d.comb += [
            # DDC
            m.submodules.ddc.input.eq(ad9203.data),
            m.submodules.ddc.frequency.eq(2415919),     # 1.440MHz
            m.submodules.ddc.rate.eq(0),
            m.submodules.ddc.shift.eq(0),
            
            # DACs
            m.submodules.dac_l.in_port.eq(m.submodules.ddc.out_i),
            m.submodules.dac_r.in_port.eq(m.submodules.ddc.out_q),
            pdm_l.eq(m.submodules.dac_l.out_port),
            pdm_r.eq(m.submodules.dac_r.out_port),
            
            # PDM outputs to LEDs
            rgb_led.r.eq(pdm_l),
            rgb_led.g.eq(pdm_r),
            
            # PDM outputs
            pdm_out.l.eq(pdm_l),
            pdm_out.r.eq(pdm_r)
        ]
        
        # restart bootloader with press of button
        m.d.sync += [
            programn.eq(usrbtn)
        ]

        return m

# if synthesizing hardware
if __name__ == "__main__":
    # add custom ADC support resources to std platform
    platform = OrangeCrabR0_2Platform()
    platform.add_resources([
        Resource("ad9203", 0,
            Subsignal("clk",    Pins("T17", dir="i"), Clock(48e6)),
            Subsignal("data",   Pins("M18 N17 N15 B10 B9 C8 B8 A8 H2 J2", dir="i")),
            Attrs(IO_TYPE="LVCMOS33", SLEWRATE="FAST")
        ),
        
        Resource("pdm_out", 0,
            Subsignal("l",   Pins("R18", dir="o")),
            Subsignal("r",   Pins("N16", dir="o")),
            Attrs(IO_TYPE="LVCMOS33", SLEWRATE="FAST")
        )
    ])
    
    # doit!
    platform.build(top(), do_program=False)