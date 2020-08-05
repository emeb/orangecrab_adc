# demods.py - audio rate demodulators
# 2020-08-03 E. Brombaugh

from nmigen import *
from r2p import *
from dcb import *
import enum

class DemodType(enum.Enum):
	AM = 0
	SYNC_AM = 1
	USB = 2
	LSB = 3
	ULSB = 4
	NBFM = 5
	RAW = 6

class demods(Elaboratable):
    def __init__(self, dsz = 16):
        # save params
        self.dsz = dsz
        self.dc_coeff = 10
        
        # ports
        self.input_i = Signal(signed(dsz))
        self.input_q = Signal(signed(dsz))
        self.ena = Signal()
        self.type = Signal(DemodType)
        self.out_l = Signal(signed(dsz))
        self.out_r = Signal(signed(dsz))
        self.valid = Signal()
        
    def elaborate(self, platform):
        m = Module()
                
        # hook up rect->polar
        m.submodules.r2p = r2p(dsz = self.dsz, psz = self.dsz)
        r2p_mag = Signal(unsigned(self.dsz))
        r2p_angle = Signal(signed(self.dsz))
        r2p_valid = Signal()
        m.d.comb += [
            m.submodules.r2p.input_x.eq(self.input_i),
            m.submodules.r2p.input_y.eq(self.input_q),
            m.submodules.r2p.ena.eq(self.ena),
            r2p_mag.eq(m.submodules.r2p.mag),
            r2p_angle.eq(m.submodules.r2p.angle),
            r2p_valid.eq(m.submodules.r2p.valid)
        ]
        
        #--------------------------------------------------------
        # AM
        #--------------------------------------------------------
        # DC block on mag output to remove carrier
        m.submodules.am_dcb = dcb(dsz=self.dsz, dc_coeff=self.dc_coeff)
        am = Signal(signed(self.dsz))
        am_valid = Signal()
        m.d.comb += [
            m.submodules.am_dcb.input.eq(r2p_mag),
            m.submodules.am_dcb.ena.eq(r2p_valid),
            am.eq(m.submodules.am_dcb.output),
            am_valid.eq(m.submodules.am_dcb.valid)
        ]
             
        #--------------------------------------------------------
        # NBFM
        #--------------------------------------------------------
        # differentiate angle to get raw frequency
        angle_d1 = Signal(signed(m.submodules.r2p.psz))
        rfrq = Signal(signed(m.submodules.r2p.psz))
        r2p_valid_d1 = Signal()
        m.d.sync += r2p_valid_d1.eq(r2p_valid)
        with m.If(r2p_valid):
            m.d.sync += [
                angle_d1.eq(r2p_angle),
                rfrq.eq(m.submodules.r2p.angle - angle_d1)
            ]
        
        # DC Block on to remove residual freq error
        m.submodules.fm_dcb = dcb(dsz=self.dsz, dc_coeff=self.dc_coeff-3)
        rfm = Signal(signed(self.dsz))
        rfm_valid = Signal()
        m.d.comb += [
            m.submodules.fm_dcb.input.eq(rfrq),
            m.submodules.fm_dcb.ena.eq(r2p_valid_d1),
            rfm.eq(m.submodules.fm_dcb.output),
            rfm_valid.eq(m.submodules.fm_dcb.valid)
        ]
        
        # De-emphasis (simple 1st-order LPF)
        nbfm_de_acc = Signal(signed(self.dsz+3))
        nbfm_valid = Signal()
        m.d.sync += nbfm_valid.eq(rfm_valid)
        with m.If(rfm_valid):
            m.d.sync += nbfm_de_acc.eq(nbfm_de_acc - (nbfm_de_acc>>7) + rfm)
        nbfm = Signal(signed(self.dsz))
        m.d.comb += nbfm.eq(nbfm_de_acc>>3)
        
        #--------------------------------------------------------
        # Output mux
        #--------------------------------------------------------
        with m.Switch(self.type):
            with m.Case(DemodType.AM):
                m.d.sync += [
                    self.out_l.eq(am),
                    self.out_r.eq(am),
                    self.valid.eq(am_valid)
                ]
            with m.Case(DemodType.NBFM):
                m.d.sync += [
                    self.out_l.eq(nbfm),
                    self.out_r.eq(nbfm),
                    self.valid.eq(nbfm_valid)
                ]
            with m.Case(DemodType.RAW):
                m.d.sync += [
                    self.out_l.eq(self.input_i),
                    self.out_r.eq(self.input_q),
                    self.valid.eq(self.ena)
                ]
            with m.Default():
                m.d.sync += [
                    self.out_l.eq(self.input_i),
                    self.out_r.eq(self.input_q),
                    self.valid.eq(self.ena)
                ]
        
        return m
