# Editable UR5e CNC machine-tending cell

**The receiving jaws close first in both directions.** On load, the gripper holds the blank against the chuck seat until the chuck jaws reach their clamped position. On retrieval, the chuck holds the blank until the gripper closes on the exposed end. The door may start closing only after the chuck owns the blank, the fingers have opened, and the entire arm and gripper have retracted clear of the doorway and the door’s full travel.

## Cell and editable assets

The saved `CNC Machine Tending` project uses Choreonoid. Its `project.cnoid` contains an empty World. The supplied source note identifies the Cyberbotics Webots R2025a UR5e. The local mesh set includes OBJ pieces for the base, shoulder, upper arm, forearm and all three wrists. Ancillary textures are absent. The cell and checks below are proposed work.

- Translate the supplied `UR5e.proto` into an editable native `.body`. Preserve the six revolute joints, parent chain, joint order, axes, origins, limits, mesh scales and link-local mesh poses. Reference the original OBJ pieces directly, using native material colors. Package those files with `LICENSE-Apache-2.0.txt` and `SOURCE.txt`. Resolve every mesh and motion reference relative to the portable project, using only supplied assets and installed tools.
- Fix the base facing the machine opening. Add a flange-mounted parallel gripper with two moving fingers, an enclosure with a horizontal-axis three-jaw chuck, a laterally sliding door, separate raw and finished V-trays, and simple fixed guard panels. Define the chuck axis and seat in the machine frame, the grip center in the flange frame and each nest in its tray frame. Expose jaw travel and door endpoints as editable joint positions.
- Use one cylindrical blank throughout. Start with an editable Ø30 × 80 mm blank, a 25 mm chuck grip at one end and a separate finger grip at the exposed end. Place the two tray nests to either side of the loading approach. Solve pick, place, insertion and retreat on the imported chain. Adjust fixture poses to fit the reachable path.

## Saved cycle

Save synchronized, editable Choreonoid motion tracks for the arm, fingers, chuck jaws, door and blank on one 50 Hz timeline. Keep the editable waypoints and transfer events with the local track generator. Use a single scripted owner for the blank. At each transfer preserve its world pose, then drive it from the receiving frame. Derive the free blank’s replay track from these transfers so scrubbing to a frame reproduces the same state as playing through it.

| Stage | Motion and condition for advancing |
|---|---|
| Pick | Begin with the door fully open, the chuck open and empty, and the blank in the raw nest. Close the fingers on the exposed grip band, transfer raw tray → gripper, then lift clear. |
| Load | Approach on the chuck axis and insert to the seat. Hold the arm still. With seating and alignment in tolerance, close all three chuck jaws on their band. At the clamped position transfer gripper → chuck. Open the fingers, then withdraw axially. |
| Close and reopen | Reach the exterior park pose. Check the chuck still owns the seated blank, the gripper is open and empty, and every arm link and finger clears the opening and the swept door volume. Hold the robot there for the full close, a brief dwell and the full reopen. |
| Retrieve | After the door reaches fully open, approach the exposed grip band with the chuck still clamped. Close the fingers, transfer chuck → gripper, then open all chuck jaws. Withdraw the blank axially only after the jaws clear it. |
| Place | Lower the same blank into the finished nest. Transfer gripper → finished tray at the supported pose, open the fingers, retract and park. |

Generate a transition only when its conditions are met. On a missed seat, incomplete jaw travel or blocked door path, hold the preceding state and identify the failed condition. The closed-door dwell represents elapsed time only. The part retains its shape throughout.

## Verification and replay

- Reopen the saved project. Compare native flange pose with source-chain forward kinematics at zero and at a bent-arm pose. Jog each of the six joints to check axis direction and mesh attachment. Sample the actual replay at pickup and lift, immediately before and after each chuck handoff, at exterior park, at mid-stroke and both door endpoints, and after final release and retreat. Record joint positions, finger and jaw travel, door displacement, owner and blank pose in the relevant receiving frame.
- Use proposed replay tolerances of 1 mm and 1° for seating, grip alignment and pose continuity across a transfer. Check constant relative pose throughout each carry and clamp interval. Confirm the finished tray retains the blank after the gripper leaves and the raw nest is empty.
- Sample each saved frame for joint limits and unintended interference along interpolated travel, including the carried blank. Allow only the intended finger, jaw, seat and nest contacts at the corresponding stages. For door motion, build the swept volume from the sliding panel geometry and its full stroke. Require at least 10 mm modeled clearance to the parked robot, open fingers and clamped blank before emitting the close track. Exercise an early close request and an early chuck-release request. Both must hold their preceding state. Record minimum clearance, the closest body pair and the frame where it occurs.
- Include local opening and replay instructions with the project. Verify them from a relocated copy with the reference folder unavailable. Open `project.cnoid`, enable the synchronized motion items, rewind to zero, play the cycle, then scrub to the documented handoff and door timestamps. Include how to edit the named targets and regenerate the tracks locally.
- Label the replay as **scripted kinematic attachment**. Report measured poses, jaw travel and sampled clearances. Grip force, frictional retention, cutting and guarding performance are outside the replay’s evidence. All motion and replay checks await implementation.
