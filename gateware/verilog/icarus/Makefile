# Makefile for Icarus Verilog simulation
# 02-11-2019 E. Brombaugh

# sources
SOURCES = 	tb_ocadc.v ../trellis/ocadc.v ../src/ddc_14.v \
        ../src/tuner_2.v ../src/tuner_slice_1k.v ../src/cic_dec_4.v \
        ../src/sat_flag.v ../src/sat.v ../src/fir8dec_par.v \
        ../src/demods.v ../src/r2p.v ../src/dcb.v \
        ../src/pdm_dac.v

# top level
TOP = tb_ocadc

# r2p
R2P = tb_r2p

# Executables
VLOG = iverilog
WAVE = gtkwave
TECH_LIB = /opt/openfpga/yosys/share/yosys/ecp5/cells_sim.v

# targets
all: $(TOP).vcd

wave: $(TOP).vcd $(TOP).gtkw
	$(WAVE) $(TOP).gtkw
	
$(TOP).vcd: $(TOP)
	./$(TOP)

$(TOP): $(SOURCES)
	$(VLOG) -D icarus -o $(TOP) $(SOURCES)
	
$(R2P).vcd: $(R2P)
	./$(R2P)

$(R2P): $(R2P).v ../src/r2p.v
	$(VLOG) -D icarus -o $(R2P) $(R2P).v ../src/r2p.v
	
clean:
	rm -rf a.out *.obj $(RPT) $(TOP) $(TOP).vcd $(R2P) $(R2P).vcd
	
