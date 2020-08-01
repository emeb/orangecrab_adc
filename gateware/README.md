# Gateware
This directory contains gateware for the OrangeCrab ADC project. There are
two different approaches taken:

## Verilog
This is a design based on Verilog source code taken from previous projects. 
To build it:

    cd verilog/trellis
    make

This will generate the .dfu file needed for programming the OrangeCrab. To
program use the following command:

    make dfu

## nMigen
This is a design based on nMigen source code. The architecture of this is
nearly identical to that of the Verilog design, but the HDL used is very
different. To build it:

    cd nmigen
    python3 top.py
    cd build
    source build_top.sh
    cp top.bit top.dfu
    dfu-suffix -v 1209 -p 5af0 -a top.dfu

This will generate the raw bitstream .bit file and the .dfu file needed for
programming the OrangeCrab. To program use the following command:

    dfu-util -D top.dfu

