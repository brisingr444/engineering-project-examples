"""Build the physical assembly. Run from the project root in bundled FreeCAD Python."""
from runtime import *
import InvoluteGearFeature

d=App.newDocument('PlanetaryGearbox')
d.Label='Meridian 05 | Planetary gearbox'
sheet=d.addObject('Spreadsheet::Sheet','Dimensions')
for row,(alias,value) in enumerate([('CaseOD','104 mm'),('FaceWidth','12 mm'),('PinCircle','45 mm'),('CoverCircle','94 mm'),('ModuleSize','1 mm'),('Pressure','20 deg'),('MeshLash','0.10 mm')],1):
    sheet.set('A'+str(row),alias)
    sheet.set('B'+str(row),value)
    sheet.setAlias('B'+str(row),alias)
sheet.Label='Design dimensions'
library=d.addObject('App::DocumentObjectGroup','PartLibrary')
assembly=d.addObject('App::Part','Gearbox')
assembly.Label='Meridian 05 | Assembled'
def group(label):
    g=d.addObject('App::Part',label)
    assembly.addObject(g)
    return g
case=group('Stationary'); front=group('InputCartridge'); carrier=group('OutputCarrier'); plategrp=group('ServicePlate')
stations=[group('PlanetStation'+str(i+1)) for i in range(3)]
steel=(0.60,0.68,0.73); dark=(0.19,0.26,0.31); teal=(0.16,0.39,0.43); brass=(0.78,0.55,0.24); light=(0.74,0.78,0.81)
def body(name,color):
    b=d.addObject('PartDesign::Body',name); library.addObject(b)
    b.addProperty('App::PropertyColor','DisplayColour','Presentation')
    b.DisplayColour=color
    if b.ViewObject:b.ViewObject.ShapeColor=color
    return b
def hide_old(b):
    for f in b.Group:
        if f.ViewObject: f.Visibility=False
    if b.Tip and b.Tip.ViewObject: b.Tip.Visibility=True
def inst(b,g,name,x=0,y=0,z=0,angle=0,placement=None):
    l=d.addObject('App::Link',name);l.LinkedObject=b;g.addObject(l)
    l.Placement=placement or pose(x,y,z,angle)
    return l
def loop(sk,pts):
    for a,b in zip(pts,pts[1:]+pts[:1]):
        sk.addGeometry(Part.LineSegment(V(*a,0),V(*b,0)),False)
def turn(name,profile,color):
    b=body(name,color)
    sk=b.newObject('Sketcher::SketchObject',name+'Section')
    sk.Placement.Rotation=App.Rotation(V(1,0,0),90)
    sk.Placement=App.Placement(V(),App.Rotation(V(1,0,0),90))
    loop(sk,profile)
    f=b.newObject('PartDesign::Revolution',name+'Turn');f.Profile=sk;f.ReferenceAxis=(sk,['V_Axis']);f.Angle=360
    return b
def tube(name,ri,ro,z,h,color):
    return turn(name,[(ri,z),(ro,z),(ro,z+h),(ri,z+h)],color)
def drill(b,name,rad,h,base,direction=V(0,0,1)):
    f=b.newObject('PartDesign::SubtractiveCylinder',name);f.Radius=rad;f.Height=h
    f.Placement=App.Placement(base,App.Rotation(V(0,0,1),direction));return f
def holes(b,name,n,radius,rad,z,h,phase=0):
    for i in range(n):
        drill(b,name,rad,h,polar(radius,phase+360*i/n)+V(0,0,z))
def socket(b,r,z,h):
    f=b.newObject('PartDesign::SubtractivePrism','HexSocket');f.Polygon=6;f.Circumradius=r;f.Height=h;f.Placement.Base=V(0,0,z)
    f.Placement=pose(z=z)
def makegear(name,n,internal=False):
    print('Building',name,flush=True)
    b=body(name,brass if internal else steel)
    if internal:
        blank=cylinder(b,'RingBlank',43,0,12)
        blank.setExpression('Height','Dimensions.FaceWidth')
    sk=InvoluteGearFeature.makeInvoluteGear(name+'Involute')
    b.addObject(sk)
    shift=.1/(4*math.tan(math.radians(20)))*(1 if internal else -1)
    # Compensate the profile shift in tip and root radii to preserve full-depth envelopes.
    add=1+(shift if internal else -shift);ded=1.25+(-shift if internal else shift)
    sk.ExternalGear=not internal;sk.NumberOfTeeth=n
    sk.setExpression('Modules','Dimensions.ModuleSize');sk.setExpression('PressureAngle','Dimensions.Pressure')
    sk.ProfileShiftCoefficient=shift;sk.RootFilletCoefficient=.30
    sk.AddendumCoefficient=add;sk.DedendumCoefficient=ded
    f=b.newObject('PartDesign::Pocket' if internal else 'PartDesign::Pad',name+'Face')
    f.Profile=sk;f.Length=12;f.setExpression('Length','Dimensions.FaceWidth')
    if internal:f.Reversed=True
    if n==27:drill(b,'SpacerBore',7,12,V())
    return b
def cylinder(b,name,r,z,h):
    f=b.newObject('PartDesign::AdditiveCylinder',name);f.Radius=r;f.Height=h;f.Placement=pose(z=z);return f
ring=makegear('Ring72',72,True)
housing=tube('Housing',38,52,-7,26,teal)
# Drive the housing outside diameter directly in its axial section.
hs=housing.Group[0]
idx=hs.addConstraint(Sketcher.Constraint('DistanceX',0,2,52.0))
hs.setExpression('Constraints[%d]'%idx,'Dimensions.CaseOD / 2')
# Match the upper outer corner to the same diameter during parameter changes.
idx=hs.addConstraint(Sketcher.Constraint('DistanceX',2,1,52.0))
hs.setExpression('Constraints[%d]'%idx,'Dimensions.CaseOD / 2')
# Constrain all remaining profile coordinates so the entire turned wall changes together.
for line,point in [(1,1),(1,2)]:
    idx=hs.addConstraint(Sketcher.Constraint('DistanceX',line,point,52.0))
    hs.setExpression('Constraints[%d]'%idx,'Dimensions.CaseOD / 2')
drill(housing,'RingSeat',43.03,19,V(0,0,-7));holes(housing,'CoverTappings',6,47,2,-7,26)
dog=turn('M4DogPoint',[(0,0),(1.35,0),(1.35,1.8),(1.97,1.8),(1.97,10),(0,10)],dark);socket(dog,1.12,8.4,2)
for i in range(3):
    a=30+120*i;vec=polar(1,a)
    drill(housing,'RadialThread',2.02,12,vec*41+V(0,0,6),vec)
    pocket_axis=polar(1,a-2.5)
    drill(ring,'DogPocket',1.45,2.4,pocket_axis*41.1+V(0,0,6),pocket_axis)
    inst(dog,case,'RingLock',placement=App.Placement(vec*41.3+V(0,0,6),App.Rotation(V(0,0,1),vec)))
inst(housing,case,'CaseShell');inst(ring,case,'FixedRing',angle=0)
sun=makegear('Sun18',18)
cylinder(sun,'InputShoulder',6.3,-11,11);cylinder(sun,'InputJournal',4.995,-47,36)
inst(sun,front,'SunInput')
planet=makegear('Planet27',27)
drill(planet,'InboardBearingSeat',8.01,5,V());drill(planet,'OutboardBearingSeat',8.01,5,V(0,0,7))
# Index dimples lie on the front faces, away from bearing seats.
drill(planet,'PlanetTimingDot',.48,.35,V(10.5,0,0));drill(sun,'SunTimingDot',.38,.35,V(7,0,0))
# First sun tooth points outward. An odd planet has its opposite space inward.
# An internal tooth on +X must face a planet space: rotate ring half a ring pitch.
d.FixedRing.Placement=pose(angle=2.5)
rear=turn('CarrierShaft',[(0,13),(32,13),(32,18),(10,18),(10,21),(7.495,21),(7.495,64),(0,64)],steel)
fp=tube('CarrierBridge',11,32,-6,5,steel)
holes(rear,'PinTapping',3,22.5,3,13,5);holes(fp,'PinSupport',3,22.5,4.01,-6,5)
holes(fp,'BridgeBoltHole',3,22.5,1.65,-6,5,60)
for i in range(3):
    p=polar(22.5,60+120*i); f=fp.newObject('PartDesign::SubtractiveCone','FlushSeat')
    f.Radius1=3.15;f.Radius2=1.65;f.Height=1.5;f.Placement=pose(p.x,p.y,-6)
    f=cylinder(rear,'IntegralPost',3.6,-1,14);f.Placement=pose(p.x,p.y,-1)
    drill(rear,'PostTapping',1.51,7,p+V(0,0,-1))
inst(rear,carrier,'OutputShaft');inst(fp,plategrp,'FrontCarrierPlate')
pin=turn('PlanetPin',[(0,-5.8),(3.995,-5.8),(3.995,-.94),(3.66,-.94),(3.66,-.46),(3.995,-.46),(3.995,13),(2.99,13),(2.99,17.8),(0,17.8)],steel)
socket(pin,1.5,-5.8,2)
pbolt=turn('BridgeScrew',[(0,-6),(3,-6),(1.49,-4.49),(1.49,4),(0,4)],dark);socket(pbolt,1.05,-6,1.1)
def bearing(name,ri,ro,w):
    # Single envelope with recessed shields around continuous inner and outer lands.
    return turn(name,[(ri,0),(ri+1,0),(ri+1,.25),(ro-1,.25),(ro-1,0),(ro,0),(ro,w),(ro-1,w),(ro-1,w-.25),(ri+1,w-.25),(ri+1,w),(ri,w)],light)
pb=bearing('PlanetBearing',4,8,5)
ps=tube('PlanetInnerSpacer',4.02,5.0,5,2,brass)
washer=tube('PlanetThrustWasher',4.01,5,-.45,.45,brass)
rw=tube('RearThrustWasher',4.01,5,12,1,brass)
clip=tube('PinClip',3.68,5.1,-.93,.46,dark)
slot=clip.newObject('PartDesign::SubtractiveBox','ClipOpening');slot.Length=6;slot.Width=2.2;slot.Height=1;slot.Placement=pose(0,-1.1,-1)
for i,g in enumerate(stations):
    ang=120*i;p=polar(22.5,ang); x,y=p.x,p.y
    inst(pin,carrier,'Axle'+str(i+1),x,y)
    inst(planet,g,'PlanetWheel'+str(i+1),x,y,angle=ang)
    for z in (0,7):inst(pb,g,'PlanetRace',x,y,z)
    inst(ps,g,'InnerSleeve',x,y);inst(rw,carrier,'RearWasher',x,y)
    inst(washer,g,'NoseWasher',x,y);inst(clip,g,'Circlip',x,y)
    p=polar(22.5,ang+60);inst(pbolt,plategrp,'PlateScrew',p.x,p.y)
# Shoulder on each cover bears on the inner-side outer race. External annular caps hold the other end.
fc=turn('InputCover',[(13.01,-32),(18,-32),(18,-11),(52,-11),(52,-7),(42.95,-7),(42.95,-6.5),(8,-6.5),(8,-11),(12,-11),(13.01,-11)],teal)
rc=turn('OutputCover',[(11,18.6),(37.96,18.6),(37.96,19),(52,19),(52,23),(22,23),(22,44),(16.01,44),(16.01,21),(11,21)],teal)
holes(fc,'CoverClearance',6,47,2.2,-11,4);holes(rc,'RearClearance',6,47,2.2,19,4)
inst(fc,front,'ServiceCover');inst(rc,case,'RearCover')
ib=bearing('InputBearing',5,13,8);ob=bearing('OutputBearing',7.5,16,9)
for z in [-30,-19]:inst(ib,front,'InputRace',z=z)
for z in [21,33]:inst(ob,carrier,'OutputRace',z=z)
for name,g,ri,ro,z,h in [('InputInnerSpacer',front,5.01,6,-22,3),('InputOuterSpacer',front,12,13,-22,3),('OutputInnerSpacer',carrier,7.51,8.5,30,3),('OutputOuterSpacer',carrier,15,16,30,3),('InputLockCollar',front,5,6.8,-32,2),('OutputLockCollar',carrier,7.5,9.4,42,2),('FrontThreadedGland',front,8,13,-32,2),('RearThreadedGland',case,11,16,42,2)]:
    inst(tube(name,ri,ro,z,h,dark),g,name+'Installed')
bolt=turn('CoverSocketScrew',[(0,0),(3.5,0),(3.5,4),(1.98,4),(1.98,14),(0,14)],dark);socket(bolt,1.74,0,2.3)
for i in range(6):
    p=polar(47,60*i)
    inst(bolt,front,'FrontCoverScrew',p.x,p.y,-15)
    inst(bolt,case,'RearCoverScrew',placement=App.Placement(p+V(0,0,27),App.Rotation(V(1,0,0),180)))
print('Recomputing physical assembly',flush=True);d.recompute()
for b in library.Group:
    if b.Shape.isNull() or len(b.Shape.Solids)!=1 or 'Invalid' in b.Tip.State:raise ValueError((b.Name,b.Tip.State))
    hide_old(b)
    if b.ViewObject:b.Visibility=False
if library.ViewObject:library.Visibility=False
for l in d.Objects:
    if l.TypeId=='App::Link' and l.ViewObject:l.Visibility=True
from presentation import visible_assembly
visible_assembly(d)
if Gui:
    Gui.updateGui();Gui.activeDocument().activeView().viewAxonometric();Gui.activeDocument().activeView().fitAll()
d.saveAs(MODEL);print('SAVED',len(library.Group),'masters',len(assembly.Shape.Solids),'solids',flush=True)

