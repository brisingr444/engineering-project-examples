# RP2040 USB-C Bench DAQ / Controller — Initial Draft
Original circuit and layout in an empty KiCad project. Unbuilt and untested; not USB-certified. No firmware, external power input, PD or isolated/overvoltage-rated inputs.
## Bench connections
Top view, count from the square pad marked 1, in the direction of the other pads.
* J1: USB-C device and sole supply. The shell is grounded. Each CC contact has its own 5.1 kΩ sink. D+ and D− use both plug orientations, low-capacitance TVS and 27 Ω series termination.
* J2 pins 1–8: GND, ADC0/GP26, GND, ADC1/GP27, GND, ADC2/GP28, GND, ADC3/GP29.
* J3 pins 1–10: GND, GP6, GP7, GP8, GP9, GP10, GP11, GP12, GP13, GND.
* J4 pins 1–4: GND, 3V3 OUT, SDA/GP4, SCL/GP5. I2C0 pull-ups 4.7 kΩ. Do not backfeed.
* J5 pins 1–5: 3V3 sense only, SWDIO, GND, SWCLK, RUN. Hold BOOT and pulse RESET for the ROM USB loader.
Use common ground, short leads and low-impedance analogue sources. Inputs 0–3.3 V only while powered. No precision rating.
## Design basis
Raspberry Pi, [Hardware design with RP2040](https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf), release 2 §§2.1–2.5: C5–C10 for six IOVDD pins, C11 USB_VDD, C12 ADC_AVDD, C13–C14 DVDD, C15 flash. C16/C17 bypass VREG_IN/OUT. ADC uses the untrimmed 3.3 V supply. Separate 1.1 V core net.
Winbond W25Q16JV, SN package, 16 Mbit QSPI. [Winbond product guide](https://www.winbond.com/productResource-files/Winbond%20Serial%20Flash%20Product%20Brief.pdf). Native symbol from wide SOIC variant; footprint overridden for narrow SOIC.
[Abracon drawing 456603 rev B](https://abracon.com/datasheets/ABM8-272-T3.pdf) pp. 3–4: 12 MHz, CL=10 pF. Two 15 pF caps present 7.5 pF in series; assume 2.5 pF stray. 1 kΩ drive limiter. Startup and margin not measured.
[Diodes AP2112](https://www.diodes.com/datasheet/download/AP2112.pdf): 1 µF ceramic input/output minimum design target, fitted 2.2 µF 25 V X7R (Murata GRM21BR71E225KA73L); effective capacitance under bias still to verify. VBUS sees 2.2 µF directly. This is not an inrush measurement. Budget whole board below 100 mA before USB configuration; external load not guaranteed until MCU/flash peak consumption and USB state are verified. At 5.25 V in, 3.3 V out and 100 mA, predicted LDO loss ≈195 mW, excluding quiescent current. Do not draw regulator nameplate current from J4.
[GCT USB4085](https://gct.co/connector/usb4085): top-mount installation, horizontal cable mating. [TI TPD2EUSB30 SLVSAC2G](https://www.ti.com/lit/ds/symlink/tpd2eusb30.pdf) p.3: three-pad DRT; keep return short at entry.
## Attribution and models
Standard symbols, footprints and referenced model paths: KiCad library contributors; CC BY-SA 4.0 with KiCad library exception. Embedded symbols and footprint instances retain their source geometry. J1 uses the KiCad 10 stock 16-contact USB2 receptacle and matched USB4085 footprint (SH = grounded shell). The 0.85 mm contact pitch and 0.70 mm lands require 0.15 mm land-to-land clearance within J1; external copper retains the 0.20 mm class spacing. Original starter had no schematic or populated PCB. No third-party board layout was imported. CSV BOM links each fitted reference to footprint and source.
The runner lacks the standard KiCad 3D model directory: **all fitted references in Bench-BOM.csv lack verified local models**. Mounting holes are mechanical, not fitted parts. Do not interpret a board-only render as assembly verification.

## Layout basis and prototype checks
Four copper layers, 1.6 mm nominal: F signal / L2 GND / L3 3V3 / B signal. Nominal outer dielectric 0.130 mm, Er 4.1, copper 35 µm. USB trunk on F.Cu: 0.20 mm trace / 0.20 mm edge gap over L2. A first-order coupled-microstrip estimate gives roughly 90 ohms differential; confirm stack with the fabricator. The mirrored connector contacts require short local branches; the DP branch uses B.Cu and one transfer via. Do not infer certified impedance from DRC. Signal routing stays off both internal planes. Filled/capped ground via at the QFN exposed pad: confirm via-in-pad process and stencil with assembler.

## Portable footprint sources
The 15 modules in the ten project-local .pretty libraries (including the M2.5 mounting hole) are unmodified copies from the installed KiCad 10 stock footprint tree selected by KICAD10_FOOTPRINT_DIR in the KiCad 10.0.5 runner. Upstream: [KiCad Footprint Library](https://gitlab.com/kicad/libraries/kicad-footprints), KiCad library contributors. [Library license and design exception](https://www.kicad.org/libraries/license/); CC BY-SA 4.0 text included in KiCad-CC-BY-SA-4.0.txt. Footprint IDs and model references are unchanged; this revision does not bundle 3D models.
