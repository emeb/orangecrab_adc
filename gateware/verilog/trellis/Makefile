# Makefile for trellis tools + yosys + nextpnr
# 07-12-20 E. Brombaugh

# src directory
VPATH = ../src/

SRC =	ocadc.v ../src/ddc_14.v ../src/tuner_2.v ../src/tuner_slice_1k.v \
        ../src/cic_dec_4.v ../src/sat_flag.v ../src/sat.v ../src/fir8dec_par.v \
        ../src/pdm_dac.v

# project stuff
PROJ = ocadc
PIN_DEF = ocadc.lpf
DEVICE = 25k
PACKAGE = CSFBGA285

YOSYS = yosys
NEXTPNR = nextpnr-ecp5
NEXTPNR_ARGS = --pre-pack $(SDC)
ECPPACK = ecppack
ECPBRAM = ecpbram
VERILATOR = verilator
TECH_LIB = /usr/local/share/yosys/ecp5/cells_sim.v

all: ${PROJ}.dfu

%.json: $(SRC)
	$(YOSYS) -p 'synth_ecp5 -top $(PROJ) -json $@' $(SRC)

%.config: %.json $(PIN_DEF) 
	$(NEXTPNR) --json $< --textcfg $@ --$(DEVICE) --package $(PACKAGE) --lpf $(PIN_DEF)

%.bit: %_ram.config
	$(ECPPACK) --compress --freq 38.8 --input $< --bit $@

%.svf: %.config
	$(ECPPACK) --compress --freq 38.8 --input $< --svf $@

%.dfu : %.bit
	cp $< $@
	dfu-suffix -v 1209 -p 5af0 -a $@

prog: $(PROJ).dfu
	dfu-util -D $(PROJ).dfu

jtag: $(PROJ).svf
	openocd -f openocd_jlink.ocd -c "svf -tap lfe5u25.tap -quiet $(PROJ).svf ; shutdown"
	
lint: $(SRC)
	$(VERILATOR) --lint-only -Wall --top-module $(PROJ) $(TECH_LIB) $(SRC)

clean:
	rm -f *.json *.config *.rpt *.bit *.svf *.dfu *.hex

.SECONDARY:
.PHONY: all prog clean
