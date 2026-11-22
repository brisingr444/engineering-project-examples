[Download this editable project ZIP](industrial-distribution-grid.zip)

Extract the complete project folder before opening it. The source files are also available below.

ZIP SHA-256: `92d57389e403af7d6e71ddb690d0f190184d002a70198d66dd112a2231c1346e`

# Industrial distribution grid
An original, editable 33-bus teaching network for PowerSystem. One 110 kV utility connection feeds two 33 kV primary sections. Six two-winding transformers and 26 lines serve four industrial areas. Follow the logistics feeder from B16 Vehicle yard to B17 EV depot PCC. The B25 rooftop PV connects on the fabrication side, not on the depot feeder.

## Open the project
1. Extract the archive. Use a compatible PowerSystem desktop to open **industrial-grid.veragrid**. No agent, account data or outside spreadsheet is required to read the saved equipment. The [PowerSystem download page](https://powersystems.dev/download/) offers a separate five-bus example and guide; it does not currently offer a public desktop installer.
2. Expand **Project → Scenarios**. Both **Baseline** and **Depot plus sun** are embedded in the same file. Under **Network model → Diagrams**, open **Industrial campus · North and South supplies**. Fit the drawing for the site overview; open **North primary to EV depot · B02–B12–B16–B17** for the depot detail. The four areas are Process, Logistics, Fabrication and Services.
3. To repeat the comparison in an edition with AC study support, select each saved scenario by name and create a balanced AC power flow in **Study cases and runs**. Use Newton–Raphson, tolerance 1e-8 and 50 iterations. Keep tap magnitude, phase, reactive-limit and remote-voltage controls and distributed slack off. Use identical equipment, taps and ratings. The original study-history database is not required or included. **checks/receipt-extracts.json** records the exact saved settings, case IDs, scenario IDs and measured equipment for each example run.

| Saved scenario | EV consumption at B17, MW / MVAr | PV injection at B25, MW / MVAr | Voltage at B17, pu | B16–B17 loading, % |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 0.60 / 0.12 | 0.20 / 0 | 0.99690 | 12.24 |
| Depot plus sun | 3.60 / 0.72 | 2.40 / 0 | 0.98781 | 73.49 |

Both cases converged. Loading is the larger terminal apparent-power magnitude divided by the same 5 MVA rating, times 100. See **depot-results.csv** for full precision, the common project hash and the two distinct native receipt hashes. These are ordinary balanced load flows in a synthetic model. They are not contingency, protection or switching assessments.

## Inputs and attribution
**inputs/site-schedule.csv** specifies the network; **inputs/operating-points.csv** specifies demand and generation. The PowerSystem private agent authored the editable model and the original electrical assumptions. **study-notes.md** explains units, transformations, limits and aggregate EV/PV representations. No benchmark dataset or third-party equipment catalog was imported. Use the included example under the accompanying LICENSE; PowerSystem and other software are separate and are not distributed here.
