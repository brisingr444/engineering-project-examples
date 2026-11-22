"""Write the as-assembled hierarchy and compare reopened STEP solids to the native instances."""
from runtime import *
import Import,json
from scipy.optimize import linear_sum_assignment
import numpy as np
d=App.openDocument(MODEL);d.recompute()
physical=[o for g in d.Gearbox.Group for o in g.Group if o.TypeId=='App::Link']
assert len(physical)==len(d.Gearbox.Shape.Solids) and len(physical)>60
path='Planetary-Gearbox.step'
if not Path(path).exists():
    Import.export([d.Gearbox],path)
s=Part.read(path)
def signature(shape):
    shape=shape.Solids[0]
    b=shape.BoundBox
    return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax,*list(shape.CenterOfMass)]
a=np.array([signature(o.Shape) for o in physical]);b=np.array([signature(o) for o in s.Solids])
cost=np.linalg.norm(a[:,None,:]-b[None,:,:],axis=2)
ii,jj=linear_sum_assignment(cost)
errors=abs(a[ii]-b[jj])
assert len(a)==len(b) and errors.max()<.01,(len(a),len(b),errors.max())
rec={'native_components':len(a),'STEP_solids':len(b),'greatest_bbox_or_centroid_coordinate_difference_mm':float(errors.max()),'shaft_centers_and_bounds_mm':{physical[i].Name:b[j].tolist() for i,j in zip(ii,jj) if physical[i].Name in ('SunInput','OutputShaft')}}
Path('Exchange-checks.json').write_text(json.dumps(rec,indent=2)+'\n')
print(rec,flush=True)

