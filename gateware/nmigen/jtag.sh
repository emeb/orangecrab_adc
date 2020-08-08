#!/bin/sh
# jtag download a bit file
openocd -f openocd_jlink.ocd -c "svf -tap lfe5u25.tap -quiet build/top.svf ; shutdown"