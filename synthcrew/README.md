[Download the editable project](synthcrew-project.zip)

Extract the ZIP before opening the project. The instructions below are also included in the archive.

SHA-256 `d135a865593fd9203a0b9324eb38d775500f7e4451af4a20df03bb0933230658`

# Two-carton inspection and reject station

Open **Retrofit_Editable.FCStd** in the SynthCrew CAD workspace. This standalone model is the revised editable assembly shown in the carousel. Verification used the FreeCAD 1.1.4 kernel.

1. Work on a copy. In **Editable state and dimensions** → **Data**, set **Pack Length**, **Pack Width** and **Pack Height** to 200 × 120 × 90 mm for the small carton or 300 × 180 × 125 mm for the large.
2. Set **Stroke Now** to 0 mm and **Reject Flag** to 0, then recompute for the belt position. Set **Stroke Now** to 576 mm and **Reject Flag** to 1, then recompute for the tray position. Keep the camera fixed.
3. Inspect the guide mounts in **Existing line** and the actuator top mounting plate in **Guided reject actuator**. Each guide seats on two editable stepped mounts that contact the conveyor stringer. An editable plate closes the stand-to-actuator gap.
4. At reject, the modeled tray contact footprint is 24,000 mm² for the small carton and 54,000 mm² for the large. In **Service / travel references**, show **Cassette extraction clearance proxy**, **Existing -Y machine service keep-out** and **Rejected receiver service side proxy**. The near-side volume clears the obstacles checked; the far-side volume intersects the service space.

**Limits:** Synthetic nominal geometry and static checks only. The mounts establish CAD contact, not rated bolted, welded or load-bearing connections. No fabrication, site fit, motion or safety validation. No AI guide insert is included.
