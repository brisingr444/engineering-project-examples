"""Measure the reopened assembly and sample the uniform spur mesh at its end face."""
from runtime import *
import json
import numpy as np
from shapely.geometry import Polygon, Point, LineString, MultiPoint
from shapely.affinity import rotate, translate
from shapely import prepare

d=App.openDocument(MODEL)
d.recompute()
physical=[o for o in d.Objects if o.TypeId=='App::Link' and o in sum([g.Group for g in d.Gearbox.Group],[])]
records={}
def record(key,v):
    records[key]=v
    print(key, str(v)[:320], flush=True)
def face_profile(obj,z,internal=False):
    faces=[f for f in obj.Shape.Faces if abs(f.BoundBox.ZMin-z)<1e-6 and f.BoundBox.ZLength<1e-6]
    wires=[w for f in faces for w in f.Wires]
    wire=max(wires,key=lambda w:len(w.Edges))
    coords=[]
    for ed in wire.OrderedEdges:
        pts=ed.discretize(Deflection=.00025) if ed.Length>.001 else [v.Point for v in ed.Vertexes]
        if ed.Orientation=='Reversed':pts=pts[::-1]
        if coords and (math.dist(coords[-1],(pts[-1].x,pts[-1].y))<math.dist(coords[-1],(pts[0].x,pts[0].y))):pts=pts[::-1]
        coords.extend((p.x,p.y) for p in pts)
    poly=Polygon(coords)
    if not poly.is_valid:poly=poly.buffer(0)
    assert poly.geom_type=='Polygon' and poly.area>150
    return poly
sun=face_profile(d.SunInput,12);planet=face_profile(d.Planet27,12);ringvoid=face_profile(d.FixedRing,12)
record('solid_count',len(physical))
record('invalid_parts',[o.Name for o in physical if len(o.Shape.Solids)!=1 or not o.Shape.isValid()])
def r_extrema(poly):
    xy=np.asarray(poly.exterior.coords)
    rr=np.hypot(xy[:,0],xy[:,1])
    return [float(rr.min()),float(rr.max())]
se,pe,re=[r_extrema(p) for p in (sun,planet,ringvoid)]
station=[d.getObject('PlanetWheel'+str(i)) for i in (1,2,3)]
centers=[o.Placement.Base for o in station]
dist=[p.Length for p in centers]
record('planet_centers_mm',[[p.x,p.y] for p in centers])
record('sun_and_ring_center_distances_mm',dist)
record('index_angles_deg',[round(math.degrees(math.atan2(p.y,p.x))%360,8) for p in centers])
record('adjacent_tip_envelope_gaps_mm',[(p-centers[(i+1)%3]).Length-2*pe[1] for i,p in enumerate(centers)])
record('radial_tip_root_clearance_mm',{'sun_tip_planet_root':dist[0]-se[1]-pe[0],'planet_tip_sun_root':dist[0]-pe[1]-se[0],'planet_tip_ring_root':re[1]-dist[0]-pe[1],'ring_tip_planet_root':re[0]-dist[0]-pe[0]})
def placed(poly,angle,x=0,y=0):
    return translate(rotate(poly,angle,origin=(0,0)),x,y)
result=[]
for a in np.linspace(0,25,9):
    ca=a/5
    s=placed(sun,a)
    for i,p in enumerate(centers):
        a0=math.degrees(math.atan2(p.y,p.x))
        c=polar(p.Length,a0+ca)
        wheel=placed(planet,a0+ca-(a-ca)*18/27,c.x,c.y)
        result.append({'sun_deg':float(a),'carrier_deg':float(ca),'station':i+1,'external_overlap_mm2':s.intersection(wheel).area,'internal_overlap_mm2':wheel.difference(ringvoid).area,'external_flank_gap_mm':s.distance(wheel),'internal_flank_gap_mm':wheel.boundary.distance(ringvoid.boundary)})
record('mesh_samples',result)
# Rotation of a planet at locked centers, to first overlap in each direction per mesh.
wheel=placed(planet,0,22.5)
def contact(internal,sign):
    lo,hi=0,1
    for _ in range(20):
        mid=(hi+lo)/2
        moving=rotate(wheel,sign*mid,origin=(22.5,0))
        hit=not ringvoid.covers(moving) if internal else sun.intersects(moving)
        if hit:hi=mid
        else:lo=mid
    return hi
record('pitch_backlash_mm',{k:13.5*math.radians(contact(flag,1)+contact(flag,-1)) for k,flag in [('sun_planet',False),('planet_ring',True)]})
# Geometric radii of the cylindrical bearing lands.
def radius(o,target):
    rr=[f.Surface.Radius for f in o.Shape.Faces if isinstance(f.Surface,Part.Cylinder)]
    return min(rr,key=lambda r:abs(r-target))
def gap(a,ra,b,rb):
    return round(2*(radius(a,ra)-radius(b,rb)),6)
record('diametral_fits_mm',{
 'ring_seat':gap(d.CaseShell,43.03,d.FixedRing,43),
 'input_OD':gap(d.ServiceCover,13.01,d.InputBearing,13),'input_journal':gap(d.InputBearing,5,d.SunInput,4.995),
 'output_OD':gap(d.RearCover,16.01,d.OutputBearing,16),'output_journal':gap(d.OutputBearing,7.5,d.OutputShaft,7.495),
 'planet_OD':gap(d.PlanetWheel1,8.01,d.PlanetBearing,8),'pin_journal':gap(d.PlanetBearing,4,d.Axle1,3.995),
 'nose_pin_support':gap(d.FrontCarrierPlate,4.01,d.Axle1,3.995)})
bb=d.FrontCarrierPlate.Shape.BoundBox
rear_face=min(f.BoundBox.ZMin for f in d.CarrierShaft.Shape.Faces if abs(f.BoundBox.ZMin-13)<1e-6 and f.BoundBox.ZLength<1e-6)
record('planet_end_gaps_mm',[d.PlanetWheel1.Shape.BoundBox.ZMin-bb.ZMax,rear_face-d.PlanetWheel1.Shape.BoundBox.ZMax])
record('pin_support_bore_mm',2*radius(d.CarrierBridge,4.01))
record('service_sun_plate_radial_gap_mm',radius(d.CarrierBridge,11)-se[1])
record('physical_envelope_mm',[round(getattr(d.Gearbox.Shape.BoundBox,k),5) for k in ('XLength','YLength','ZLength')])
record('axial_contacts_mm',{k:a.Shape.distToShape(b.Shape)[0] for k,a,b in [('ring_shoulder',d.FixedRing,d.CaseShell),('front_cover_flange',d.ServiceCover,d.CaseShell),('rear_cover_flange',d.RearCover,d.CaseShell),('front_plate_posts',d.FrontCarrierPlate,d.OutputShaft)]})
Path('Geometry-checks.json').write_text(json.dumps(records,indent=2)+'\n')
assert not records['invalid_parts']
assert max(max(s['external_overlap_mm2'],s['internal_overlap_mm2']) for s in result)<1e-5
assert all(.09<v<.11 for v in records['pitch_backlash_mm'].values())
assert all(.24<v<.26 for v in records['radial_tip_root_clearance_mm'].values())
print('Passed 54 sampled mesh pairs and backlash / tip clearance thresholds.',flush=True)

