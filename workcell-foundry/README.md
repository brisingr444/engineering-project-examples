[Download the editable project](workcell-palletizer-editable.zip)

Extract the ZIP before opening the project. The instructions below are also included in the archive.

SHA-256 `95ea21104607c8a972473e929bc45cec15a862a98f41172c975153e121746e80`

# Indexed conveyor palletizer

Editable six-carton Workcell Foundry simulation. Open **`project.cnoid`** in a compatible Windows Workcell Foundry installation with the native Choreonoid worker and Workcell Python controller. Keep this folder together. An unmodified stock Choreonoid install alone is not sufficient for the included controllers.

## Inspect and run

1. Open `project.cnoid` and confirm six cartons on the conveyor. The queue uses 52 mm center-to-center spacing. Each stop tab is 3.2 mm wide, 1.2 mm farther outboard than in the 34 mm starting version. The pickup datum remains `[0.100, -0.125, 0.750]` m.
2. Use the saved setup `engineering/setups/run.json` with **CellCPU**. Its duration is 108 s, the solver step is 2 ms, and recording is every 60 ms. Run through the Workcell native simulation workflow, not by executing the controller scripts directly.
3. In recorded results, confirm six placement commits and the loaded staggered pallet. For the placement error, compare each carton’s recorded base position with its corresponding XYZ target in the `staggered` array in `recipes.json`. Take the maximum Euclidean distance across all six cartons and the final 0.64 s of recorded positions.

The retained verification recorded 1,800 samples, six placement commits and a worst settled error of **1.499603 mm**. Both jaws registered contact during each lift. There was no sampled off-target gantry contact above 0.01 N; the trace did record the active carton touching the stop tabs during lift. This is a synthetic fixture and a discrete simulation check, not continuous clearance, a hardware result or safety validation.

**Verification note:** The qualifying run completed through Workcell’s protected saved-project simulation service after a Run-panel attempt failed in its command server. Do not treat a controller-server error as a completed run. Commands and timing are for this saved native Windows configuration; other builds and platforms were not checked here.

The scene, models, controllers and setup are byte-identical to the verified run inputs. The package contains only the final scene’s dependencies and target data, not the failed baseline, captured trace, organizational account settings, or application binaries. The trimmed bundle does not claim the archival workspace digest of the larger run snapshot.
