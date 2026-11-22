# Industrial campus operating cases

Open industrial-grid.veragrid and select **Industrial campus · North and South supplies** in either saved scenario. Trace B01 through North/B02 to Process or Logistics, or through South/B03 to Fabrication or Services. The editable diagram includes all 33 buses, 26 lines, six two-winding transformers and their connected equipment. The 24 scheduled fixed demands total 18.64 MW and 5.99 MVAr. The balanced AC snapshots use three-phase total powers.

| Operating case | B17 EV consumption (MW / MVAr) | B25 PV injection (MW / MVAr) |
|---|---:|---:|
| Baseline | 0.60 / 0.12 | 0.20 / 0.00 |
| Depot plus sun | 3.60 / 0.72 | 2.40 / 0.00 |

Both aggregates connect directly at 11 kV. The EV is a constant-P/Q load. Rooftop PV is a native static-mode generator with fixed reactive power, unity power factor, dispatch disabled and an assumed 2.5 MVA rating. These devices add to fixed load. The two source schedules are included under inputs/. Bus codes preserve the CSV identifiers.

## Teaching assumptions

The project uses a 100 MVA three-phase base, 50 Hz and scheduled line-to-line voltage bases. B01 is a single ideal voltage/angle reference at 1.02 pu and 0 rad. Its available import capacity was unspecified. The voltage review band is 0.95–1.05 pu and the continuous branch loading threshold is 100%.

| Feeder group | Segment length (km) | R (Ω/km) | X (Ω/km) | Continuous rating (MVA) |
|---|---:|---:|---:|---:|
| Process | 0.30 | 0.10 | 0.09 | 8 |
| Logistics and Fabrication | 0.25 | 0.14 | 0.10 | 6 |
| Services | 0.20 | 0.20 | 0.10 | 4 |
| B12–B16 and B16–B17 override | 0.40 | 0.16 | 0.10 | 5 |

Each 11 kV line has series impedance (R+jX) × length / 1.21 Ω in pu. Shunt admittance is zero. Drawing distances are schematic.

| Transformer class | Scheduled ratio (kV) | Scheduled rating (MVA) | Short-circuit voltage (%) | Copper / core losses (kW) | No-load current (%) |
|---|---:|---:|---:|---:|---:|
| T-N, T-S | 110/33 | 40 | 12 | 160 / 30 | 0.20 |
| T-M, T-F, T-P, T-U | 33/11 | 16 | 8 | 80 / 15 | 0.25 |

Losses and impedances are synthetic. On each unit’s MVA rating, series r = full-load copper loss in MW / rating, z = short-circuit voltage / 100, and x = √(z² − r²). Excitation conductance g = core loss in MW / rating, and susceptance b = −√[(no-load current / 100)² − g²]. Multiply r and x by 100 / rating and g and b by rating / 100 for circuit-base pu. All taps are fixed at nominal ratio, with zero phase displacement.

## Reading the comparison

The native balanced Newton–Raphson runs use a 1e-8 pu tolerance and a 50-iteration limit. Tap, phase, remote-voltage, reactive-limit and distributed-slack controls are disabled. Compare the same B17 voltage magnitude and B16–B17 branch in depot-results.csv. Loading is 100 × max(|S from|, |S to|) / 5 MVA. Convergence, voltage and branch loading refer to the recorded snapshot.

The saved archive was reopened to check topology, loads, transformer settings and shared device IDs. Only EV P/Q and PV P differ electrically. A native offscreen render was inspected at overview and PCC detail scales. All 32 saved routes were checked against the 33 native bus label bounds. No route crossed a supplied label or exceeded the 1.5 detour review ratio. Full native symbol collision testing and live visual acceptance are unavailable. These are educational operating cases.

## Source integrity

| Retained input | SHA-256 |
|---|---|
| site-schedule.csv | 3b269579aab33a12c19009760b4d6d3e1c602b56dcf15c1b7181a3a0bebab04d |
| operating-points.csv | b0631e2f673d7ca866c03c5c582cd46caac9bb647d80c06d1b9ffc0c1e2d8bf2 |

### Saved drawing revision

The site overview groups Process and Logistics under the North supply and Fabrication and Services under the South supply. For a closer view of the charging depot, open **North primary to EV depot · B02–B12–B16–B17**. Both scenarios include both sheets. The drawings were revised after the two reported studies. All electrical record payloads are unchanged; the original case and receipt identities still refer to the original studies. See **checks/diagram-revision.json**.
