# Makefile for Icarus Verilog simulation
# 02-11-2019 E. Brombaugh

# sources
SOURCES = 	tb_ocadc.v ../trellis/ocadc.v ../src/ddc_14.v \
        ../src/tuner_2.v ../src/tuner_slice_1k.v ../src/cic_dec_4.v \
        ../src/sat_flag.v ../src/sat.v ../src/fir8dec_par.v \
        ../src/pdm_dac.v

# top level
TOP = tb_ocadc
			
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

$(TOP): $(SOURCES) $(HEX)
	$(VLOG) -D icarus -o $(TOP) $(SOURCES)
	
clean:
	rm -rf a.out *.obj $(RPT) $(TOP) $(TOP).vcd
	
