"""Regenerate the CNC tending replay in the installed Choreonoid Python SDK."""
from pathlib import Path
import json
import math
import re

import numpy as np
import yaml
from cnoid import Base, BodyPlugin

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "cycle.json").read_text())
RATE = CONFIG["rate"]
TARGETS = {name: np.array(value) for name, value in CONFIG["targets"].items()}
TCP = np.array(CONFIG["tcp_in_flange"])
GRIP_OFFSET = np.array(CONFIG["blank_center_from_tcp_world"])
SEAT = np.array(CONFIG["seat_world"])
ORIENTATION = np.array([[1., 0., 0.], [0., 0., 1.], [0., -1., 0.]])
MODELS = ["UR5e", "CNC", "RawTray", "FinishedTray", "Guarding", "Blank"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rotation(axis, angle):
    x, y, z = axis
    cross = np.array([[0., -z, y], [z, 0., -x], [-y, x, 0.]])
    return np.eye(3) + math.sin(angle) * cross + (1 - math.cos(angle)) * (cross @ cross)


def source_chain():
    source = (ROOT / "assets/UR5e.proto").read_text()
    def vector(section, key, length):
        match = re.search(r"\b" + key + r"\s+([^\n]+)", section)
        return np.array(list(map(float, match[1].split()[:length])))
    result = []
    for joint in source.split("jointParameters HingeJointParameters {")[1:]:
        solid = joint.split("endPoint Solid {")[1].split("children [")[0]
        axis = vector(joint, "axis", 3)
        offset = vector(solid, "translation", 3)
        require(np.allclose(offset, vector(joint, "anchor", 3)), "Offset pivot")
        rest = vector(solid, "rotation", 4) if "rotation" in solid else [1, 0, 0, 0]
        result.append((offset, axis, rotation(rest[:3], rest[3]),
                       vector(joint, "minPosition", 1)[0], vector(joint, "maxPosition", 1)[0],
                       vector(joint, "maxVelocity", 1)[0]))
    require(len(result) == 6, "Expected six source joints")
    return result


CHAIN = source_chain()


def forward(q):
    p, r = np.zeros(3), np.eye(3)
    frames = [(p, r)]
    for angle, (offset, axis, rest, *_) in zip(q, CHAIN):
        p = p + r @ offset
        r = r @ rotation(axis, angle) @ rest
        frames.append((p, r))
    return frames


def inverse(target):
    """Elbow-up solution with flange +Y down and jaw grip band parallel to X."""
    x, y, z = target
    z0, y1, elbow, wrist, y4, z5 = [joint[0] for joint in CHAIN]
    lateral = y1[1] + elbow[1] + y4[1]
    radial = math.sqrt(x*x + y*y - lateral*lateral)
    pan = math.atan2(y, x) - math.atan2(lateral, radial)
    u, v = radial - z5[2], z + .1 + TCP[1] - z0[2]
    a, b = elbow[2], wrist[2]
    bend = math.acos((u*u + v*v - a*a - b*b) / (2*a*b))
    rest = math.atan2(CHAIN[1][2][0, 2], CHAIN[1][2][0, 0])
    lift = math.atan2(u, v) - math.atan2(b*math.sin(bend), a+b*math.cos(bend)) - rest
    q = np.array([pan, lift, bend, math.pi/2 - 2*rest - lift - bend,
                  -math.pi/2, pan - math.pi/2])
    p, r = forward(q)[-1]
    grip = p + r @ (TCP + [0., .1, 0.])
    require(np.linalg.norm(grip-target) < 1e-6 and np.allclose(r, ORIENTATION, atol=1e-6),
            "Forward kinematics disagrees with the requested grip pose")
    return q, grip, r


def matches(actual, desired):
    return np.linalg.norm(actual - desired) <= .001


def door_permission(owner, finger, jaw, clearance):
    return owner == "chuck" and finger >= .019999 and jaw <= 1e-8 and clearance >= .010


def release_permission(owner, finger, jaw, door):
    return owner == "gripper" and finger <= 1e-8 and jaw <= 1e-8 and door >= .719999


def shape_bounds(element, origin, attitude):
    local_rot = element.get("rotation", [1, 0, 0, 0])
    r = attitude @ rotation(local_rot[:3], math.radians(local_rot[3]))
    p = origin + attitude @ np.array(element.get("translation", [0, 0, 0]))
    geom = element["elements"][0]["geometry"]
    if geom["type"] == "Box":
        ext = np.abs(r) @ (np.array(geom["size"])/2)
    else:
        axis = np.abs(r[:, 1])
        radius = geom["radius"]
        ext = axis*geom["height"]/2 + radius*(1 if geom["type"] == "Capsule"
                                                else np.sqrt(np.maximum(0, 1-axis**2)))
    return p - ext, p + ext


def door_gap(q, finger, blank):
    arm = BODIES["UR5e"]["links"]
    frames = forward(q)
    flange_p = frames[-1][0] + frames[-1][1] @ [0, .1, 0]
    frames.append((flange_p, frames[-1][1]))
    for link in arm[-2:]:
        p = np.array(link["translation"]) + np.array(link["jointAxis"]) * finger
        frames.append((flange_p + frames[7][1] @ p, frames[7][1]))
    bounds = []
    for link, (origin, r) in zip(arm, frames):
        shapes = link["elements"]
        if shapes[0]["type"] == "Visual":
            shapes = shapes[1]["elements"]
        for element in shapes:
            bounds.append((link["name"], *shape_bounds(element, origin, r)))
    bounds.append(("Blank", *shape_bounds(BODIES["Blank"]["links"][0]["elements"][0],
                                          blank, np.eye(3))))
    door = BODIES["CNC"]["links"][-1]
    best = (float("inf"), "")
    for i, element in enumerate(door["elements"]):
        lo, hi = shape_bounds(element, np.array(door["translation"]), np.eye(3))
        sweep = np.array(door["jointAxis"]) * door["jointRange"][1]
        for name, low, high in bounds:
            gap = np.maximum(0., np.maximum(low-np.maximum(hi, hi+sweep),
                                            np.minimum(lo, lo+sweep)-high))
            best = min(best, (float(np.linalg.norm(gap)), f"{name}/SlidingDoor[{i}]"))
    return best


BODIES = {name: yaml.safe_load((ROOT / f"models/{name}.body").read_text()) for name in MODELS}


def generate():
    tracks = {name: [] for name in ("UR5e", "CNC", "Blank")}
    events = CONFIG["frames"]
    owner = "raw"
    blank = TARGETS["raw"] + GRIP_OFFSET
    local_grip = None
    previous_q = None
    finger, jaw, door = .02, .022, .72
    old_pos = TARGETS[events[0]["target"]]
    prior_frame = 0
    samples = []
    min_gap = None
    for idx, event in enumerate(events):
        pos = TARGETS[event["target"]]
        end = round(event["time"] * RATE)
        old_joints = np.array([finger, jaw, door])
        new_joints = np.array([event.get(k, v) for k, v in zip(("finger","jaw","door"), old_joints)])
        if new_joints[2] < door:
            gap, pair = door_gap(previous_q, finger, blank)
            require(door_permission(owner, finger, jaw, gap), f"Door inhibited at {event['stage']}")
            require(np.array_equal(pos, old_pos), "Arm must remain parked throughout door travel")
            min_gap = dict(frame=prior_frame, metres=gap, pair=pair)
        if new_joints[1] > jaw:
            require(release_permission(owner, finger, jaw, door), "Chuck release inhibited")
        if new_joints[0] > finger:
            require(owner in ("chuck", "finished"), "Finger release inhibited")
        for k in range(0 if idx == 0 else prior_frame+1, end+1):
            fraction = (k-prior_frame)/(end-prior_frame) if end != prior_frame else 1.
            blend = fraction**2 * (3 - 2*fraction)
            finger, jaw, door = old_joints + blend*(new_joints-old_joints)
            target = old_pos + blend*(pos-old_pos)
            q, grip, r = inverse(target)
            for j, (_, _, _, low, high, speed) in enumerate(CHAIN):
                require(low <= q[j] <= high, f"Joint {j} limit at {k}")
                if previous_q is not None:
                    require(abs(q[j]-previous_q[j])*RATE <= speed, f"Joint {j} speed at {k}")
            previous_q = q
            if owner == "gripper":
                blank = grip + r @ local_grip
            if door < .719999:
                require(matches(grip, TARGETS["park"]) and owner == "chuck", "Door travel hold")
            receiver = event.get("receive") if k == end else None
            if receiver == "gripper":
                expected = "raw" if owner == "raw" else "chuck"
                require(owner in ("raw", "chuck") and finger < 1e-8 and
                        matches(grip, blank-GRIP_OFFSET) and door >= .719999 and
                        (expected != "chuck" or jaw < 1e-8), "Gripper acquisition inhibited")
                local_grip = r.T @ (blank-grip)
            elif receiver == "chuck":
                require(owner == "gripper" and jaw < 1e-8 and finger < 1e-8 and
                        matches(blank + [.04, 0, 0], SEAT), "Chuck acquisition inhibited")
            elif receiver == "finished":
                require(owner == "gripper" and matches(blank, TARGETS["finished"] + GRIP_OFFSET),
                        "Finished nest acquisition inhibited")
            if receiver:
                owner = receiver
            tracks["UR5e"].append([*q, finger, finger])
            tracks["CNC"].append([jaw, jaw, jaw, door])
            tracks["Blank"].append([*blank, 1., 0., 0., 0.])
            if k == end or (receiver or event.get("receive")) and k == end-1 or (
                    old_joints[2] != new_joints[2] and k == (end+prior_frame)//2):
                samples.append(dict(frame=k, time=k/RATE, stage=event["stage"], owner=owner,
                                    arm=q.round(8).tolist(), fingers_m=float(finger),
                                    jaws_m=float(jaw), door_m=float(door), blank_m=blank.tolist()))
        old_pos, prior_frame = pos, end
    require(not door_permission("gripper", .0, .0, .10) and
            not door_permission("chuck", .02, .0, .005), "Early close test")
    require(not release_permission("chuck", .02, .0, .72), "Early release test")
    require(owner == "finished" and matches(blank, TARGETS["finished"]+GRIP_OFFSET), "End state")
    return tracks, samples, min_gap


def write_motion(path, values, free):
    component = "MultiSE3Seq" if free else "MultiValueSeq"
    content = "LinkPosition" if free else "JointDisplacement"
    header = ["type: CompositeSeq", "content: BodyMotion", "formatVersion: 2.0", "components:",
              f"  - type: {component}", f"    content: {content}", f"    frameRate: {RATE}",
              f"    numFrames: {len(values)}", f"    numParts: {1 if free else len(values[0])}"]
    if free:
        header.append("    SE3Format: XYZQWQXQYQZ")
    header.append("    frames:")
    for row in values:
        line = "[" + ", ".join(f"{x:.10g}" for x in row) + "]"
        header.append("      - " + ("["+line+"]" if free else line))
    path.write_text("\n".join(header)+"\n", encoding="utf-8")


def assemble(tracks):
    folder = ROOT / "motions"
    folder.mkdir(exist_ok=True)
    world = BodyPlugin.WorldItem()
    world.setName("World")
    Base.RootItem.instance.addChildItem(world)
    for name in MODELS:
        item = BodyPlugin.BodyItem()
        require(item.load(str(ROOT/f"models/{name}.body")), f"Body load failed for {name}")
        item.setName(name)
        world.addChildItem(item)
        item.setChecked(True)
        if name in tracks:
            values = tracks[name]
            path = folder / (name+".seq")
            write_motion(path, values, name == "Blank")
            track = BodyPlugin.BodyMotionItem()
            require(track.load(str(path), "BODY-MOTION-YAML"), f"Motion load failed for {name}")
            track.setName(name+" cycle")
            item.addChildItem(track)
            track.setChecked(True)
            if name == "Blank":
                item.body.rootLink.p = np.array(values[0][:3])
            else:
                for j, q in enumerate(values[0]):
                    item.body.joint(j).q = q
            item.body.calcForwardKinematics()
            item.notifyKinematicStateChange()
            item.storeInitialState()
    bar = Base.TimeBar.instance
    bar.setFrameRate(RATE)
    bar.setTimeRange(0., CONFIG["frames"][-1]["time"])
    bar.setTime(0.)
    require(Base.ProjectManager.instance.saveProject(str(ROOT/"project.cnoid")), "Project save failed")


if __name__ == "__main__":
    tracks, samples, clearance = generate()
    assemble(tracks)
    (ROOT/"motions/samples.json").write_text(json.dumps(
        {"method":"Scripted kinematic attachment", "door_sweep_lower_bound":clearance,
         "samples":samples}, indent=2)+"\n")
    print("Saved frames per track:", len(tracks["Blank"]), "door sweep:", clearance)
