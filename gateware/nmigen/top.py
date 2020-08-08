# top.py - top level of IF quadrature decimating downconverter
# 2020-08-01 E. Brombaugh

from nmigen import *
from adc_domain import *
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
        
        # instantiate the ADC domain
        m.submodules.adc_domain = DomainRenamer("sync_adc")(adc_domain())
        
        # create a clock domain in the renamed domain and connect
        # to ADC clock
        sync_adc = ClockDomain("sync_adc", reset_less=True)
        m.domains += sync_adc
        m.d.comb += [
            sync_adc.clk.eq(ad9203.clk),
            #sync_adc.rst.eq(0)
        ]

        # hook up ADC clock domain
        m.d.comb += [
            # ADC Clock domain
            m.submodules.adc_domain.adc_data.eq(ad9203.data),
            pdm_out.l.eq(m.submodules.adc_domain.pdm_l),
            pdm_out.r.eq(m.submodules.adc_domain.pdm_r),
            
            # PDM outputs to Blue LED
            rgb_led.b.eq(m.submodules.adc_domain.pdm_l),
            
            # ADC Clock status output to Green LED
            rgb_led.g.eq(m.submodules.adc_domain.clkstat)
        ]
        
        # Main Clock status output to Red LED
        clk_div = Signal(23)
        m.d.sync += clk_div.eq(clk_div + 1)
        m.d.comb += rgb_led.r.eq(clk_div[-1])
        
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