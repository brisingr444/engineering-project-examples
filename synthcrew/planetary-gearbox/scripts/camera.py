"""Store an orthographic Coin camera and native FreeCAD finish materials in the assembly."""
from runtime import *
import copy
import zipfile
from xml.etree import ElementTree as ET

with zipfile.ZipFile(MODEL) as z:doc=ET.fromstring(z.read('Document.xml'))
objects=doc.findall('./ObjectData/Object')
scene=ET.Element('Document',SchemaVersion='1',HasExpansion='1')
ET.SubElement(scene,'Expand')
providers=ET.SubElement(scene,'ViewProviderData')
def prop(obj,n):return obj.find("./Properties/Property[@name='"+n+"']")
palette=App.newDocument('Palette')
colors={}
for obj in objects:
    c=prop(obj,'DisplayColour')
    if c is None:continue
    packed=int(c.find('PropertyColor').get('value'));key='Finish%08X'%packed
    colors[obj.get('name')]=key
    tip=prop(obj,'Tip')
    if tip is not None:colors[tip.find('Link').get('value')]=key
    if palette.getObject(key):continue
    material=App.Material();material.DiffuseColor=tuple(((packed>>s)&255)/255 for s in (24,16,8))
    material.Shininess=30
    swatch=palette.addObject('Part::Feature',key);swatch.addProperty('App::PropertyMaterialList','Finish')
    swatch.Finish=[material]
style=Path('.synthcrew/view-settings.FCStd');palette.saveAs(str(style))
included={}
with zipfile.ZipFile(style) as z:
    data=ET.fromstring(z.read('Document.xml'))
    for obj in objects:
        flag=prop(obj,'Visibility')
        if flag is None:continue
        name=obj.get('name')
        vp=ET.SubElement(providers,'ViewProvider',name=name,expanded='1' if name=='Gearbox' else '0')
        props=ET.SubElement(vp,'Properties');props.append(copy.deepcopy(flag))
        if name in colors:
            key=colors[name]
            swatch=data.find("./ObjectData/Object[@name='"+key+"']")
            entry=copy.deepcopy(prop(swatch,'Finish'));entry.attrib={'name':'ShapeAppearance','type':'App::PropertyMaterialList','status':'1'}
            src=entry.find('MaterialList');old=src.get('file');src.set('file',key+'.material')
            included[key+'.material']=z.read(old);props.append(entry)
        props.set('Count',str(len(props)))
providers.set('Count',str(len(providers)))
toward=V(1,-1,-1);toward.normalize()
right=V(0,0,1)-toward*toward.z;right.normalize()
up=toward.cross(right)
rotation=App.Rotation(right,up,toward,'ZXY')
pos=V(0,0,8.5)+toward*300
axis=rotation.Axis
settings='OrthographicCamera {\n viewportMapping ADJUST_CAMERA\n position %g %g %g\n orientation %g %g %g %.12g\n nearDistance 185\n farDistance 415\n aspectRatio 1\n focalDistance 300\n height 188\n}\n'%(*pos,*axis,rotation.Angle)
ET.SubElement(scene,'Camera',settings=settings)
# Validate Coin's native camera record and the model's projected framing.
from pivy import coin
inp=coin.SoInput();inp.setBuffer('#Inventor V2.1 ascii\n'+settings)
node=coin.SoDB.readAll(inp);cam=node.getChild(0)
assert abs(cam.height.getValue()-188)<1e-5
for x in (-52,52):
    for y in (-52,52):
        for z in (-55.5,55.5):
            v=V(x,y,z);assert abs(v.dot(up))<94 and abs(v.dot(right))<94
dst=Path(MODEL).with_suffix('.staging')
with zipfile.ZipFile(MODEL) as z,zipfile.ZipFile(dst,'w',compression=zipfile.ZIP_DEFLATED) as out:
    for entry in z.infolist():
        if entry.filename!='GuiDocument.xml' and entry.filename not in included:out.writestr(entry,z.read(entry))
    for key,data in included.items():out.writestr(key,data)
    out.writestr('GuiDocument.xml',ET.tostring(scene,encoding='utf-8',xml_declaration=True))
dst.replace(MODEL)
print('Stored native isometric camera,',len(included),'finishes and',len(providers),'visibility records.')

