[Download the editable project](siliconforge-telemetry-capture.zip)

Extract the ZIP before opening the project. The instructions below are also included in the archive.

SHA-256 `dfa90877f979f3b4676eb72e32a9460b4b3f7f55da792dedd46d7b9ce2e4ef28`

# Capturing FPGA packets when the host falls behind

Editable, synthetic SystemVerilog example: a four-slot FPGA packet recorder with a local 32-bit ready/valid input and APB4 readout. Open this directory in **SiliconForge** and select `rtl/telemetry_capture.sv`. The RTL top is `telemetry_capture`; the unchanged scoreboard is `tb/tb_telemetry_capture.sv`. See [CONTRACT.md](CONTRACT.md) for the register map and reset semantics.

From this directory, with Icarus Verilog and VVP on PATH:

```sh
iverilog -g2012 -s tb_telemetry_capture -o telemetry.vvp \
  rtl/telemetry_capture.sv tb/tb_telemetry_capture.sv
vvp telemetry.vvp
```

Expect `PASS telemetry`, seven fully read packets checked in order (including the post-reset read), and a maximum of four queued. In SiliconForge open **Waveforms → Open trace** and select the generated `waveform.vcd`. Select `in_valid`, `in_ready`, `in_data`, `apb_readback`, `PRDATA`, `queued` and `packet_retire`. The first DATA access at 825 ns is a header read; the final payload read at 975 ns frees the slot. Use 824/834 ns and 974/984 ns as before/after cursors for those respective edges.

To reproduce the deliberate failure in a **separate duplicate** of this directory, apply `patch -p1 < early-retirement-demo.patch`, then repeat the same external commands. The first DATA read now retires early; the unchanged bench rejects the next header word. Do not apply the patch to the working example.

The evidence is directed, single-clock simulation; the regression ran outside SiliconForge and the VCD was imported for inspection. This is not a native run receipt, board deployment, hardware throughput or timing closure. It uses no vendor IP, AXI, DMA or CDC.
