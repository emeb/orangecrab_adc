# fir8dec.py - FIR decimate by 8
# 2020-07-31 E. Brombaugh

from nmigen import *
import math as math
import numpy as np
import scipy.signal as signal
import matplotlib as mpl
import matplotlib.pyplot as plt
from fir8dec_slice import *

class fir8dec(Elaboratable):
    def __init__(self, isz = 16, osz = 16):
        # save params
        self.isz = isz
        self.osz = osz
        self.fir_len = 246
        fir_bits = 19   # leave @ 19 for better quant - correct in HW scaling
        self.lut_asz = 8
        self.lut_dsz = 16
        self.agrw = fir_bits - self.lut_dsz # HW scaling for coeff sz
        
        # specify filter transition band - center and width
        tb_ctr = 1/16   # normalized transition band center
        tb_width = 0.4  # normalized transition band width

        # calc filter coeffs
        pass_corner = tb_ctr - (tb_ctr*tb_width/2)
        stop_corner = tb_ctr + (tb_ctr*tb_width/2)
        fir_bands = [0, pass_corner, stop_corner, 0.5]
        b = signal.remez(self.fir_len, fir_bands, [1, 0])
        coeff_scl = 2**(fir_bits-1)
        fir_coeff = np.floor(b*coeff_scl + 0.5)

        # dump out FIR details
        if 0:
            W, H = signal.freqz(fir_coeff)
            passband_max = np.max(np.abs(H))
            stopband_idx = np.nonzero(W/np.pi > (stop_corner+0.1))
            stopband_max = np.max(np.abs(H[stopband_idx]))
            print('Stopband Atten = ', 20*np.log10(passband_max/stopband_max), 'dB')
            plt.figure()
            plt.plot(W/(2*np.pi), 20*np.log10(np.abs(H)))
            plt.grid()
            plt.xlabel("Freq (Hz)")
            plt.ylabel("dB")
            plt.title("fir4dec response (close to continue)")
            plt.show()
            
            # compute coeff word size
            coeff_bits = 1+np.ceil(np.log2(np.max(np.abs(fir_coeff))))
            print('Max coeff bits = ', coeff_bits)

            # compute worst-case sum for hardware sizing
            acc_sum = np.sum(32768*np.abs(fir_coeff))
            acc_bits = 1+np.ceil(np.log2(acc_sum))
            print('Max accumulator bits = ', acc_bits)

        # stuff into array
        LUT = np.zeros(2**self.lut_asz, dtype=np.int)
        LUT[0:self.fir_len] = fir_coeff
            
        #print(LUT)
        
        # create the coeff LUT - read only
        self.coeffs = Memory(width = self.lut_dsz, depth = 2**self.lut_asz, init = LUT)
        self.coeff_r = self.coeffs.read_port(transparent=False)
        
        # create the input buffer - read/write
        self.buffer = Memory(width = 2*self.isz, depth = 2**self.lut_asz)
        self.buffer_w = self.buffer.write_port()
        self.buffer_r = self.buffer.read_port()        
        
        # ports
        self.input_i = Signal(signed(isz))
        self.input_q = Signal(signed(isz))
        self.ena = Signal()
        self.output_i = Signal(signed(osz))
        self.output_q = Signal(signed(osz))
        self.valid = Signal()
        
    def elaborate(self, platform):
        m = Module()
        
        # write address counter
        w_addr = Signal(self.lut_asz)
        with m.If(self.ena):
            m.d.sync += w_addr.eq(w_addr + 1)
            
        # FIR state machine
        coeff_end = Signal()
        mac_ena = Signal()
        dump = Signal()
        r_addr = Signal(self.lut_asz)
        c_addr = Signal(self.lut_asz)
        ena_d1 = Signal()
        m.d.sync += ena_d1.eq(self.ena)
        with m.FSM():
            with m.State('WAIT'):
                with m.If(ena_d1 & (w_addr[:3] == 7)):
                    m.next = 'MAC'
                    m.d.sync += [
                        mac_ena.eq(1),
                        r_addr.eq(w_addr),
                        c_addr.eq(0),
                        coeff_end.eq(0)
                    ]
                    
            with m.State('MAC'):
                with m.If(coeff_end == 0):
                    m.d.sync += [
                        r_addr.eq(r_addr - 1),
                        c_addr.eq(c_addr + 1),
                        coeff_end.eq(c_addr == (self.fir_len-1))
                    ]
                with m.Else():
                    m.next = 'DUMP'
                    m.d.sync += [
                        mac_ena.eq(0),
                        dump.eq(1)                        
                    ]
                    
            with m.State('DUMP'):
                m.next = 'WAIT'
                m.d.sync += dump.eq(0)
        
        # input buffer
        m.submodules.buffer_w = self.buffer_w
        m.d.comb += [
            self.buffer_w.addr.eq(w_addr),
            self.buffer_w.data.eq(Cat(self.input_i,self.input_q)),
            self.buffer_w.en.eq(self.ena)
        ]
        m.submodules.buffer_r = self.buffer_r
        ird = Signal(signed(self.isz))
        qrd = Signal(signed(self.isz))
        m.d.comb += [
            self.buffer_r.addr.eq(r_addr),
            ird.eq(self.buffer_r.data[:self.isz]),
            qrd.eq(self.buffer_r.data[self.isz:])
        ]
        
        # FIR Coeff LUT
        m.submodules.coeff_r = self.coeff_r
        c_data = Signal(signed(self.lut_dsz))
        m.d.comb += [
            self.coeff_r.addr.eq(c_addr),
            c_data.eq(self.coeff_r.data)
        ]
        
        # delay control signals
        mac_ena_pipe = Signal(2)
        dump_pipe = Signal(3)
        m.d.sync += [
            mac_ena_pipe.eq(Cat(mac_ena,mac_ena_pipe[0])),
            dump_pipe.eq(Cat(dump,dump_pipe[:2]))
        ]
        
        # MACs
        m.submodules.mac_i = fir8dec_slice(isz = self.isz, csz = self.lut_dsz, osz = self.osz, agrw = self.agrw)
        m.submodules.mac_q = fir8dec_slice(isz = self.isz, csz = self.lut_dsz, osz = self.osz, agrw = self.agrw)
        m.d.comb += [
            m.submodules.mac_i.input.eq(ird),
            m.submodules.mac_q.input.eq(qrd),
            m.submodules.mac_i.coeff.eq(c_data),
            m.submodules.mac_q.coeff.eq(c_data),
            m.submodules.mac_i.mac_ena.eq(mac_ena_pipe[1]),
            m.submodules.mac_q.mac_ena.eq(mac_ena_pipe[1]),
            m.submodules.mac_i.dump.eq(dump_pipe[1]),
            m.submodules.mac_q.dump.eq(dump_pipe[1]),
            self.output_i.eq(m.submodules.mac_i.output),
            self.output_q.eq(m.submodules.mac_q.output),
            self.valid.eq(dump_pipe[2])
        ]
            
        return m