# Open and run the example

Extract the whole project directory. In SiliconForge choose **File → Open project** and select this directory. Open `rtl/axis_packet_switch.sv` for the design and `tb/tb_axis_packet_switch.sv` for the self-checking bench.

With Icarus Verilog and vvp installed and on PATH, run this from the extracted project root:

    sh sim/run.sh

The run writes to `build/`. In the Waveforms view, use **Open trace…** and select `build/contention.vcd`. To inspect a previously generated example without running a simulator, open `example-output/contention.vcd` instead. Select the output-ready bus, the contenders and grant for output 0, and the clock. Watch the ready bit for output 0 return high before its accepted final beat at 65 ns. The owner then advances, while all four inputs are still requesting service.

The trace is from a directed simulation of this RTL and bench, not a measurement on an FPGA. The stand-alone runner uses Icarus, not a SiliconForge simulation service. See README.md for the signal convention, FIFO depth, arbitration limits and reset behavior.
