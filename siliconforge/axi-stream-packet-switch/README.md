[Download this editable project ZIP](axi-stream-packet-switch.zip)

Extract the complete project folder before opening it. The source files are also available below.

ZIP SHA-256: `264d4b84c8d9a838c37b63ebb152540b00638c8f34f96f9531df87bd0bb8a2f2`

# Four-lane AXI-Stream packet switch

Open [the switch RTL](rtl/axis_packet_switch.sv) in SiliconForge and select
`axis_packet_switch` as the synthesis top. For simulation, add
[the self-checking bench](tb/tb_axis_packet_switch.sv) and select
`tb_axis_packet_switch`.

## Stream contract

All lanes share `aclk`. A rising edge with `aresetn` low flushes every FIFO,
releases every grant and restores input 0 to first priority on every output.
Outside reset a lane transfers on a rising edge with both TVALID and TREADY
high. The source drives data, destination, last and valid. The sink drives
ready. The switch receives on `s_axis_*` and sends on `m_axis_*`.

| Signal suffix | Packed width | Lane i |
| --- | ---: | --- |
| tdata | 128 | `[32*i +: 32]`, four valid bytes |
| tdest | 8 | `[2*i +: 2]`, preserved output number |
| tlast, tvalid, tready | 4 each | `[i]` |

Lane 0 occupies the least significant slice. A source holds valid and payload
stable through a stall, keeps destination constant within a frame, and may
insert gaps between beats.

Each input queues two complete beats. Only its head can request an output,
so a stalled head also delays traffic behind it. Each output scans requests
in cyclic order, locks its first offered beat on a stall, and retains the
source across empty-FIFO gaps until TLAST transfers. The input following the
winner then has first priority. With four persistent requesters, each gets
one turn per four completed frames. A receiver stall or a source withholding
TLAST can extend that turn indefinitely. Disjoint routes can each deliver
one beat per clock after filling.

## Reproduce

Run `sh sim/run.sh` from the project root with Icarus Verilog and vvp.
The runner compiles the two editable sources, exits on failure, and generates
`build/contention.vcd`. In the 20–140 ns trace, contenders bit i identifies
input i requesting output 0. Grant identifies the selected input. All four
request at 25 ns, output 0 holds its beat until the 65 ns transfer, then
round-robin service advances on every clock.

The bench compares each delivered beat to the recorded source handshakes.
Packet counts increment on accepted TLAST. In the observed run, the first
drain reported 194 input and 194 output packets. Two further single-beat
packets were buffered and flushed by reset. Fresh traffic drained at 4 in
and 4 out. The bench printed per-port counts and PASS. Local Verilator RTL
lint and generic Yosys synthesis with a structural check also passed.
