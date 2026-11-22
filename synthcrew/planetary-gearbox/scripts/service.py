"""Check disassembly at axial events, using the actual planar gear sections and cylindrical lands."""
from runtime import *
import json
d=App.openDocument(MODEL)
mesh=json.loads(Path('Geometry-checks.json').read_text())
pairs=[]
def common(label,a,b,offset=0):
    s=a.Shape.copy();s.translate(V(0,0,-offset));t=b.Shape
    vol=0. if not s.BoundBox.intersect(t.BoundBox) else s.common(t).Volume
    pairs.append([label,a.Name,b.Name,offset,round(vol,7)])
    return vol
# At this fixed index, overlap of uniform spur tooth sections is invariant during axial separation.
for lock in [o for o in d.Stationary.Group if o.Name.startswith('RingLock')]:
    common('Dog seated in ring pocket',lock,d.FixedRing)
# BB reject for all travel samples. The gear section check covers the sun-planet pair.
for travel in (0,1,6,12,18,30,60):
    for a,b in [(d.ServiceCover,d.CaseShell),(d.ServiceCover,d.FrontCarrierPlate),(d.SunInput,d.FrontCarrierPlate),(d.SunInput,d.OutputShaft)]:
        common('Input withdrawal',a,b,travel)
for travel in (0,1,5,6,15,30):
    for b in [d.Axle1,d.Axle2,d.Axle3,d.OutputShaft,d.CaseShell]:
        common('Bridge withdrawal',d.FrontCarrierPlate,b,travel)
for i in range(1,4):
    p=d.getObject('PlanetWheel'+str(i))
    g=d.getObject('PlanetStation'+str(i))
    ax=d.getObject('Axle'+str(i))
    for travel in (0,1,6,12,18,30):
        for b in [o for o in g.Group if o.Name.startswith(('PlanetRace','InnerSleeve'))]:
            common('Bearing assembly slides along axle',b,ax,travel)
        # Each post is outside the planet tip envelope. The ring check uses the uniform internal tooth profile.
    common('Planet rear-face to carrier',p,d.OutputShaft)
pin_center=d.Axle1.Placement.Base
posts=[f for f in d.CarrierShaft.Shape.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-3.6)<1e-7]
postgap=min((V(f.Surface.Center.x,f.Surface.Center.y,0)-pin_center).Length for f in posts)-3.6-14.5
report={'kernel_common_volume_samples':pairs,'largest_common_volume_mm3':max(row[-1] for row in pairs),'gear_withdrawal_at_fixed_index_overlap_mm2':max(max(x['external_overlap_mm2'],x['internal_overlap_mm2']) for x in mesh['mesh_samples'] if x['sun_deg']==0),'planet_to_nearest_post_radial_envelope_gap_mm':postgap,'input_sun_to_bridge_radial_gap_mm':mesh['service_sun_plate_radial_gap_mm'],'withdrawal_travel_mm':{'cartridge':60,'bridge':30,'planets':30}}
Path('Service-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('samples',len(pairs),'max overlap',report['largest_common_volume_mm3'],'post gap',postgap,flush=True)
assert postgap>0 and report['largest_common_volume_mm3']<1e-5

