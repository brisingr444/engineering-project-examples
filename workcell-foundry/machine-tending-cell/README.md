[Download this editable project ZIP](machine-tending-cell.zip)

Extract the complete project folder before opening it. The source files are also available below.

ZIP SHA-256: `815b3b84e9fa4989ced7ab19543b8983326c3733a18bba665c52a712f252ccbb`

# CNC machine tending with the UR5e

Open `project.cnoid` in Workcell or Choreonoid with the Body plugin enabled. Keep the project folder together when moving it. The arm, enclosure, trays, blank, guard rails and motion items are ordinary editable native assets. The original Cyberbotics R2025a PROTO, OBJ files, license and provenance note are in `assets/`.

## Play and inspect

Expand **World**. Show the six body items. Enable the motion items under **UR5e**, **CNC** and **Blank** together. Select all three motion items if your Choreonoid configuration follows selection. Set the time bar to 0–35.8 s at 50 frames/s. Rewind and press Play. Scrub all three tracks together. Frame numbers below start at zero.

| Time | Frame | State to inspect |
|---:|---:|---|
| 2.00 s | 100 | Open fingers straddle the rear grip band in the blue raw tray. |
| 2.50 s | 125 | Fingers close. The gripper takes the blank and lifts it through 4.00 s. |
| 10.00 s | 500 | Blank nose meets the chuck seat. The gripper holds still. |
| 10.60 s | 530 | Three chuck jaws have closed on the forward 25 mm. The chuck takes the blank. |
| 11.20 s | 560 | Fingers are open. The arm withdraws along the chuck axis and moves to park. |
| 15.00 s | 750 | Arm parked, fingers open, blank seated. The door can begin closing. |
| 15.70 / 16.40 s | 785 / 820 | Door at half stroke / closed. The chuck keeps the same blank. |
| 18.10 / 18.80 s | 905 / 940 | Door at half stroke / fully reopened. The arm stays parked until fully open. |
| 23.20 s | 1160 | Fingers close on the exposed band. The gripper takes the blank while the chuck is still closed. |
| 23.80 s | 1190 | Chuck jaws have opened. The arm starts axial extraction. |
| 31.60 / 32.20 s | 1580 / 1610 | Blank reaches the green finished nest. Fingers open before the arm leaves. |
| 35.80 s | 1790 | Arm parked. The single blank remains in the finished nest. |

The cylindrical stock is 30 mm in diameter and 80 mm long. Blank ownership is a **scripted kinematic attachment**. The owner changes at an aligned pose without changing the world transform. Separate tracks animate finger and jaw closure. The dwell represents elapsed time. The replay supplies no measurements of contact force, retention under load, cutting or guard performance.

## Edit and regenerate

Edit the native bodies under `models/` for geometry. Edit `cycle.json` for named grip-center targets in world metres, times in seconds, jaw positions in metres and receiver events. The machine axis is world +X into the chuck. Its seat lies at [0.635, 0, 0.320] m. The blank center is 25 mm forward of the gripper center. The gripper jaws close across the blank and the chuck jaws move radially.

Run `tools/build_cycle.py` as the entrypoint in Workcell's installed native Choreonoid Python SDK, starting in a fresh isolated session. The script reads the bundled PROTO, solves the six-joint chain, checks forward kinematics, source joint limits, seating and handoff gates, writes the three motion tracks and saves the project. A failed gate stops generation before the tracks are written. Keep fixture targets and their physical locations consistent when editing. Run `tools/native_check.py` in a fresh native SDK session to check a relocated copy and its sampled states.

`motions/samples.json` lists the scripted owners and expected states for comparison with replay. Each arm row uses source joint order followed by the two finger displacements. Each CNC row contains three radial jaw displacements followed by the door displacement. The blank track stores its world pose at every frame, so playback can start in the middle of either handoff.

## Checks on the supplied cycle

The native SDK reopened a relocated copy with all ten world, body and motion items. The link and flange frames agreed with forward kinematics from the supplied PROTO at zero, at a bent pose and during six individual joint jogs. Across 32 native timeline samples the arm, fingers, chuck, door and blank agreed with their saved states. The last sample placed the blank center at [0.303, 0.310, 0.180] m in the finished nest.

A separate geometric check read all 1,791 saved frames at 20 ms intervals. It tested the arm’s source collision primitives, both fingers, the carried blank and the cell geometry, excluding adjacent connected arm links. The box, cylinder and capsule checks found no unintended modeled overlap at those frames. During the full door stroke the smallest bounding-volume clearance was 97 mm between the blank and the main door panel, first reached at frame 750. The specified minimum was 10 mm. These results apply to this saved geometry and trajectory.
