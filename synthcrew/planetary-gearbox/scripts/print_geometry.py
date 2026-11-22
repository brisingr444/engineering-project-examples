"""Reconstruct the print views from saved BReps, sheet settings and measured references."""
from runtime import *
from xml.etree import ElementTree as ET
from zipfile import ZipFile
import TechDraw

def print_document():
    z=ZipFile(MODEL)
    tree=ET.fromstring(z.read('Document.xml'))
    objs={n.get('name'):n for n in tree.findall('./ObjectData/Object')}
    def prop(n,k):
        return objs[n].find("./Properties/Property[@name='"+k+"']")
    def field(n,k,attr='value'):
        return list(prop(n,k))[0].get(attr)
    def vec(n,k):
        return V(*[float(field(n,k,'value'+c)) for c in 'XYZ'])
    def ls(n,k):
        return [o.get('value') for o in prop(n,k).findall('.//Link')]
    d=App.newDocument('PrintGeometry')
    refs=['InputEnd','MeridianAA','HoleLayout']
    for n in sorted(set(sum([ls(v,'Source') for v in refs],[]))):
        lk=prop(n,'LinkedObject')
        master=lk.find('XLink').get('name') if lk is not None else n
        brp=prop(master,'Shape').find('Part').get('file')
        shape=Part.Shape();shape.importBrepFromString(z.read(brp).decode('ascii'))
        if lk is not None:
            pl=prop(n,'Placement').find('PropertyPlacement')
            shape.Placement=App.Placement(V(*[float(pl.get('P'+c)) for c in 'xyz']),App.Rotation(*[float(pl.get('Q'+str(i))) for i in range(4)]))*shape.Placement
        d.addObject('Part::Feature',n).Shape=shape
    p=d.addObject('TechDraw::DrawPage','GeneralArrangement')
    t=d.addObject('TechDraw::DrawSVGTemplate','ReferenceFrame')
    t.Template=str(Path('scripts/reference-frame.svg').resolve());p.Template=t
    for n in refs:
        v=d.addObject('TechDraw::DrawViewSection' if n=='MeridianAA' else 'TechDraw::DrawViewPart',n)
        p.addView(v)
        if n=='MeridianAA':
            v.BaseView=d.InputEnd;v.SectionNormal=vec(n,'SectionNormal');v.SectionOrigin=vec(n,'SectionOrigin');v.SectionSymbol='A'
        v.Direction=vec(n,'Direction');v.XDirection=vec(n,'XDirection');v.Source=[d.getObject(s) for s in ls(n,'Source')]
        v.ScaleType='Custom';v.Scale=float(field(n,'Scale'));v.X=float(field(n,'X'));v.Y=float(field(n,'Y'))
    d.recompute()
    for n in ls('GeneralArrangement','Views'):
        if n in refs:continue
        if prop(n,'References2D') is not None:
            v=d.addObject('TechDraw::DrawViewDimension',n)
            dimtype='Diameter' if n in ('HousingDiameter','CoverBoltCircle','PinCircle') else 'DistanceY' if 'JournalDiameter' in n else 'DistanceX'
            v.Type=dimtype
            v.References2D=[(d.getObject(k.get('obj')),k.get('sub')) for k in prop(n,'References2D').findall('.//Link')]
            v.FormatSpec=field(n,'FormatSpec')
        else:
            v=d.addObject('TechDraw::DrawViewAnnotation',n)
            v.Text=[k.get('value') for k in prop(n,'Text').findall('.//String')]
            v.TextSize=float(field(n,'TextSize'))
        p.addView(v);v.X=float(field(n,'X'));v.Y=float(field(n,'Y'))
    d.recompute()
    import json
    measured=json.loads(Path('Drawing-checks.json').read_text())['raw_dimensions_mm']
    for n,value in measured.items():
        assert abs(float(d.getObject(n).getRawValue())-value)<.001,n
    z.close()
    return d

