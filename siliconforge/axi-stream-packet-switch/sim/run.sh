#!/bin/sh
set -eu
mkdir -p build
iverilog -g2012 -s tb_axis_packet_switch -o build/packet_switch.vvp \
    rtl/axis_packet_switch.sv tb/tb_axis_packet_switch.sv
vvp build/packet_switch.vvp +TRACE=build/contention.vcd
test -s build/contention.vcd
