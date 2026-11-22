"""Reopen a relocated project and sample its synchronized native timeline."""
from pathlib import Path
from copy import deepcopy
import json
import shutil
import sys
import tempfile

import numpy as np
from cnoid import Base, BodyPlugin

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tools"))
import build_cycle as cycle


def descend(item):
    child = item.childItem
    while child:
        yield child
        yield from descend(child)
        child = child.nextItem


def validate(project):
    manager = Base.ProjectManager.instance
    manager.loadProject(str(project))
    items = list(descend(Base.RootItem.instance))
    bodies = {item.name: item for item in items if isinstance(item, BodyPlugin.BodyItem)}
    tracks = [item for item in items if isinstance(item, BodyPlugin.BodyMotionItem)]
    print("Restored", list(bodies), [(t.name, t.motion.numFrames) for t in tracks], flush=True)
    cycle.require(set(bodies) == set(cycle.MODELS) and len(tracks) == 3, "Incomplete project restore")
    duration = cycle.CONFIG["frames"][-1]["time"]
    for track in tracks:
        cycle.require(track.motion.numFrames == round(duration*cycle.RATE)+1
                      and track.motion.frameRate == cycle.RATE, "Motion header")
        track.setSelected(True)
    robot = bodies["UR5e"].body
    for q in [np.zeros(6), np.array([.2, -.6, .9, -.4, .5, .3])] + list(np.eye(6)*.1):
        for j in range(6):
            robot.joint(j).q = q[j]
        robot.calcForwardKinematics()
        frames = cycle.forward(q)
        for spec, (link_p, link_r) in zip(cycle.BODIES["UR5e"]["links"], frames):
            link = robot.link(spec["name"])
            cycle.require(np.allclose(link.p, link_p, atol=1e-6) and
                          np.allclose(link.R, link_r, atol=1e-6), "Source link frame " + spec["name"])
        p, r = frames[-1]
        flange = robot.link("ToolFlange")
        cycle.require(np.linalg.norm(flange.p-p-r@[0,.1,0]) < 1e-6, "Flange origin")
        cycle.require(np.allclose(flange.R, r, atol=1e-6), "Flange orientation")
    samples = json.loads((project.parent/"motions/samples.json").read_text())["samples"]
    bar = Base.TimeBar.instance
    # Sample inside a 20 ms frame to avoid binary rounding at its left boundary.
    bar.setFrameRate(1000)
    bar.setTimeRange(0, duration)
    bar.setTime(.5)
    for row in samples:
        bar.setTime(min(duration, row["time"] + .1/cycle.RATE))
        arm = [robot.joint(j).q for j in range(8)]
        machine = [bodies["CNC"].body.joint(j).q for j in range(4)]
        blank = bodies["Blank"].body.rootLink.p
        desired_arm = row["arm"] + [row["fingers_m"]]*2
        cycle.require(np.allclose(arm, desired_arm, atol=1e-6),
                      f"Arm at {row['time']}: observed {arm}, expected {desired_arm}")
        expected = [row["jaws_m"]]*3 + [row["door_m"]]
        cycle.require(np.allclose(machine, expected, atol=1e-6),
                      f"Machine at frame {row['frame']}: observed {machine}, expected {expected}")
        cycle.require(cycle.matches(blank, row["blank_m"]), "Blank replay")
    print("Native timeline samples checked", len(samples), "final blank", blank, flush=True)


def check_early_request(stage, changes, expected_error):
    original = cycle.CONFIG["frames"]
    trial = deepcopy(original)
    next(event for event in trial if event["stage"] == stage).update(changes)
    try:
        cycle.CONFIG["frames"] = trial
        cycle.generate()
    except ValueError as error:
        cycle.require(expected_error in str(error), str(error))
        print(stage, "request held:", error)
    else:
        raise AssertionError(f"Unexpectedly allowed early request at {stage}")
    finally:
        cycle.CONFIG["frames"] = original


check_early_request("Axial withdrawal", {"door": 0}, "Door inhibited")
check_early_request("Reach exposed band", {"jaw": .022}, "Chuck release inhibited")

with tempfile.TemporaryDirectory(dir=ROOT) as copy:
    relocated = Path(copy)
    for folder in ("models", "motions", "assets"):
        shutil.copytree(ROOT/folder, relocated/folder)
    shutil.copy2(ROOT/"project.cnoid", relocated)
    validate(relocated/"project.cnoid")
