[Download the editable project](powersystem-harbor-cold-store.zip)

Extract the ZIP before opening the project. The instructions below are also included in the archive.

SHA-256 `8e5ca9e3976c92112b08039729fc19289b9e3cd202360acdc5f452d5713a7b94`

# Harbor cold-store feeder study

Two editable PowerSystem/VeraGrid models of a fictional harbor network. Both files contain the complete saved input for the same peak, T01-out, tie-closed operating point; no external workbook, account, image, or private data is required to open the network files.

| Open this file | Saved topology |
|---|---|
| `A-T01-out.veragrid` | Original shared 33 kV feed. |
| `B-dedicated-T03.veragrid` | Detached edit: B03 supplies T03 (132/33 kV, 40 MVA), then B10, the existing CB-L08 bay and L08 feeder, and the B09 cold store. |

## Reproduce the two checks

1. Open A in a PowerSystem build that reads native `.veragrid` projects. Open the main harbor one-line, then check that **T01 is out** and **CB-LV-coupler is closed**. The six active loads total **109.7 MW**; the load at B09 is **20 MW / 6 MVAr**.
2. In the study workspace, save a **balanced AC power-flow** case. Use a tolerance of **1e-8** and **50** maximum iterations, with reactive limits, transformer tap-magnitude control, transformer tap-phase control and remote voltage control enabled. Leave distributed slack disabled. Run the saved case.
3. Repeat for B without changing the controls or load. The B file’s main diagram still starts with “A” in its tab; the right-hand **T03/B10** branch identifies the edited topology.
4. Compare **T02 Port transformer B**. Use the larger terminal apparent power, `max(hypot(P_from,Q_from), hypot(P_to,Q_to))`, in MVA. The native loading-percent row uses a **100 MVA study rating**. The independent **80 MVA screen** is checked against the resulting MVA values, not substituted into the saved settings.

| Exact saved input | T02 larger terminal | At the 100 MVA study rating | At the separate 80 MVA screen |
|---|---:|---:|---:|
| A peak, T01 out + tie closed | 119.883113 MVA | 119.883113% | Above |
| B peak, T03, T01 out + tie closed | 97.087615 MVA | 97.087615% | Above |

Both retained AC solves converged. This is one synthetic, steady-state outage snapshot per topology. It is not operating or switching advice, proof of uninterrupted service or a general N-1 qualification.

## Exact shown files

```text
8506c6d62bcf5c569f2cdb4b480918de4b043e8c013372383de2d68768938e09  A-T01-out.veragrid
29d87c2e5be8d75eeec084b19c112e83593fa569bb403afa6b6fd5d4fca367b5  B-dedicated-T03.veragrid
```
