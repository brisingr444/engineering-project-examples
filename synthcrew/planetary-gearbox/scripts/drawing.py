"""Assemble an associative A3 TechDraw sheet with a meridional section."""
from runtime import *
import TechDraw, time, json
from PySide import QtCore
d=App.openDocument(MODEL)
page=d.addObject('TechDraw::DrawPage','GeneralArrangement')
template=d.addObject('TechDraw::DrawSVGTemplate','ReferenceFrame')
template.Template=str(Path('scripts/reference-frame.svg').resolve());page.Template=template
def settle(seconds=1):
    t=time.monotonic()
    while time.monotonic()-t<seconds:QtCore.QCoreApplication.processEvents();time.sleep(.035)
def placeview(n,src,dir,xd,x,y):
    v=d.addObject('TechDraw::DrawViewPart',n);v.Source=src;v.Direction=dir;v.XDirection=xd
    page.addView(v);v.X=x;v.Y=y;return v
# Section only the components intersected by y=0, plus housing fasteners on that plane.
sources=[o for g in d.Gearbox.Group for o in g.Group if o.Shape.BoundBox.YMin<=1e-6 and o.Shape.BoundBox.YMax>=-1e-6]
end=placeview('InputEnd',sources+[o for o in d.InputCartridge.Group if o.Name.startswith('FrontCoverScrew') and o not in sources],V(0,0,-1),V(1,0,0),78,195)
sec=d.addObject('TechDraw::DrawViewSection','MeridianAA');page.addView(sec);sec.BaseView=end;sec.Source=sources
sec.SectionNormal=V(0,1,0);sec.SectionOrigin=V(0,0,6);sec.Direction=V(0,1,0);sec.XDirection=V(0,0,1);sec.SectionSymbol='A'
sec.X=274;sec.Y=195
# The fixture view uses real bridge and housing plus pitch-circle datums. Visible hole centers are dimension references.
datums=d.addObject('App::DocumentObjectGroup','DrawingDatums')
pitch=[]
for name,driver in [('PinPitchCircle','Axle1'),('BoltPitchCircle','CoverTappings')]:
    c=d.addObject('Part::Circle',name);datums.addObject(c)
    c.setExpression('Radius',driver+'.Placement.Base.x');c.Placement=pose(z=-7.2)
    c.Visibility=False;pitch.append(c)
fixture=placeview('HoleLayout',[d.CaseShell,d.FrontCarrierPlate]+pitch,V(0,0,-1),V(1,0,0),78,70)
fixture.ScaleType='Custom';fixture.Scale=.65
def note(n,t,x,y,h=3.1):
    a=d.addObject('TechDraw::DrawViewAnnotation',n);a.Text=t;a.TextSize=h;page.addView(a);a.X=x;a.Y=y;return a
note('SetupNotes',['PLANET TRAIN    /    18 : 27 : 72','3 stations at 120 degrees on the pin circle','6 cover screws at 60 degrees on the bolt circle','Spur teeth   /   module 1   /   20 degrees','Fixed ring   /   sun input   /   carrier output'],146,100,3.8)
note('Captions',['INPUT END'],53,133)
note('SectionCaption',['SECTION A-A     /     THROUGH AXLE 1'],231,132)
note('FixtureCaption',['CARRIER AND CASE     /     0.65:1'],42,27)
d.recompute();settle(2)
def waitview(v):
    for i in range(90):
        if len(v.getVisibleEdges())>0:return
        settle(.4)
    raise RuntimeError('No projected edges '+v.Name)
for v in [end,sec,fixture]:waitview(v)
def dim(view,name,typ,refs,x,y,fmt=None):
    o=d.addObject('TechDraw::DrawViewDimension',name);o.Type=typ;o.References2D=[(view,r) for r in refs]
    page.addView(o);o.X=x;o.Y=y
    if fmt:o.FormatSpec=fmt
    return o
def circle(view,r):
    for i in range(len(view.getVisibleEdges())):
        e=view.getEdgeByIndex(i)
        if isinstance(e.Curve,Part.Circle) and abs(e.Curve.Radius-r)<.03:return 'Edge'+str(i)
    raise ValueError(('circle',view.Name,r))
def vertices(view):
    out=[]
    for i in range(len(view.getVisibleVertexes())):
        try:v=view.getVertexByIndex(i).Point
        except (IndexError,ValueError,RuntimeError,AttributeError):break
        out.append((i,v.x,v.y))
    return out
def span(view,n,typ,length,x,y,fmt=None,side=0):
    pts=vertices(view);ax=1 if typ=='DistanceX' else 2;cross=3-ax
    tgt=length
    hits=[(abs(a[cross]-b[cross])-.1*side*(a[1]+b[1]),a,b) for a in pts for b in pts if abs((b[ax]-a[ax])-tgt)<.00005]
    if not hits:raise ValueError((view.Name,n,length,pts[:12]))
    _,a,b=min(hits);return dim(view,n,typ,['Vertex'+str(a[0]),'Vertex'+str(b[0])],x,y,fmt)
dims=[]
dims.append(dim(fixture,'HousingDiameter','Diameter',[circle(fixture,52)],-44,18,'Ø%.0f'))
dims.append(span(sec,'CaseAxialLength','DistanceX',76,0,62))
dims.append(span(sec,'InputProjection','DistanceX',15,-57,-54,side=-1))
dims.append(span(sec,'OutputProjection','DistanceX',20,51,-54,side=1))
dims.append(span(sec,'InputJournalDiameter','DistanceY',9.99,-67,12,'Ø%.2f',side=-1))
dims.append(span(sec,'OutputJournalDiameter','DistanceY',14.99,68,12,'Ø%.2f',side=1))
# Pitch datums take their radii from the first installed axle and the first cover tapping.
dims.append(dim(fixture,'CoverBoltCircle','Diameter',[circle(fixture,47)],43,-19,'PCD Ø%.0f'))
dims.append(dim(fixture,'PinCircle','Diameter',[circle(fixture,22.5)],28,28,'PCD Ø%.0f'))
d.recompute();settle(2)
values={o.Name:float(o.getRawValue()) for o in dims}
print('dimensions',values,flush=True)
for key,target in zip(values,[104,76,15,20,9.99,14.99,94,45]):
    assert abs(values[key]-target)<.025,(key,values[key],target)
page.Visibility=False
d.save()
# Exercise a native driver and its associative dimension in memory after saving.
d.Dimensions.set('B1','106 mm');d.recompute();settle(3)
changed=round(d.CaseShell.Shape.BoundBox.XLength,4);raw=float(d.HousingDiameter.getRawValue())
print('changed diameter',changed,raw,flush=True)
assert abs(changed-106)<.002 and abs(raw-106)<.002
Path('Drawing-checks.json').write_text(json.dumps({'raw_dimensions_mm':values,'unsaved_case_OD_edit_mm':[changed,raw]},indent=2)+'\n')
from portable import portable_model
portable_model(MODEL)

