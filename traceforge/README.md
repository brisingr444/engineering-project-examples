[Download the editable project](LoopBridge-24-P1.zip)

Extract the ZIP before opening the project. The instructions below are also included in the archive.

SHA-256 `7dc81ad4cafb2708eb4537c6001963725b45639a925f6ba1bc4fcc977ea329b9`

# LoopBridge-24 P.1
An **unbuilt digital reference** for digitizing four externally powered 4–20 mA transmitter signals. The project does not excite the loops. Each has a dedicated signal and a return wire; all four returns join primary GND on the PCB. RS-485 is on a separate, isolated interface.

## Open and inspect
1. Open **LoopBridge-24.kicad_pro** in TraceForge with KiCad 10.0.5 support, or KiCad 10.0.5. Keep the adjacent project-local symbol and footprint libraries intact. Check `sha256sum -c CAD.sha256` before comparing against the reported result.
2. In Schematic Editor open the **Four passive current receivers and ADC** sheet and inspect **J10 (FIELD LOOPS)** and **U9**. J10 contacts 1–4 are LOOP1–LOOP4; contacts 5–8 are GND. Pairs: **1/5, 2/6, 3/7, 4/8**. Compare `mechanical/harness-map.csv`; `ISO_GND` belongs to the rear RS-485 interface, not J10.
3. Open the PCB. Locate J10 at the front edge and turn on **User.Drawings** for the service model. `mechanical/panel-interface.P1.pdf` and the DXFs/OBJ describe reference envelopes, not cabinet machining or mated part fit.
4. Run Electrical Rules Check and PCB Design Rules Check including schematic parity. CLI equivalents:
   ```sh
   kicad-cli sch erc --format json --exit-code-violations -o erc.json LoopBridge-24.kicad_sch
   kicad-cli pcb drc --format json --schematic-parity --exit-code-violations -o drc.json LoopBridge-24.kicad_pcb
   ```
   Inspect `violations`, `unconnected_items`, `schematic_parity` and `ignored_checks`. P.1 uses inherited rules, including five DRC exclusions. A deliberate no-connect is not an unrouted pad.

## Limits
This is the saved P.1 reference variant, not the output of the later A.1 AI request. No board was fabricated. No per-channel isolation, loop excitation, verified end-to-end communications, measured fault withstand, fit approval or field qualification. Read [engineering-limits.md](engineering-limits.md) for assumptions and checks still owed before fabrication or use. Third-party footprints retain the notices in `licenses/`.
