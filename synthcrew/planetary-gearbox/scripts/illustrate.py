"""Render the physical FreeCAD shapes for the assembly and service plates."""
from runtime import *
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from functools import lru_cache
d=App.openDocument(MODEL)
groups=d.Gearbox.Group
physical=[o for g in groups for o in g.Group if o.TypeId=='App::Link']
def shift(o):
    n=o.Name
    if n.startswith('FrontCoverScrew'):return -133
    if o in d.InputCartridge.Group:return -104
    if n.startswith('PlateScrew'):return -84
    if n=='FrontCarrierPlate':return -67
    if n.startswith(('Circlip','NoseWasher')):return -52 if n.startswith('Circlip') else -46
    if any(o in g.Group for g in groups if g.Name.startswith('PlanetStation')):return -28
    return 0
# Orthographic painter with the input to the left. All source triangles come from the installed solids.
toward=np.array([-.34,-.83,-.45]);toward/=np.linalg.norm(toward)
right=np.array([0.,0.,1.])-toward*toward[2];right/=np.linalg.norm(right)
up=np.cross(toward,right)
M=np.array([right,-up,toward]).T
@lru_cache(None)
def mesh(master):
    vertices,facets=master.Shape.tessellate(.085)
    return np.array([list(v) for v in vertices]),np.array(facets)
def font(size,bold=False):
    candidates=['Lato-Bold.ttf','DejaVuSans-Bold.ttf'] if bold else ['Lato-Regular.ttf','DejaVuSans.ttf']
    for name in candidates:
        try:return ImageFont.truetype(name,size)
        except OSError:pass
    return ImageFont.load_default()
def drawplate(exploded):
    tris=[];colors=[]
    for o in physical:
        v,f=mesh(o.LinkedObject); mat=np.array(o.Placement.toMatrix().A).reshape(4,4)
        xyz=v@mat[:3,:3].T+mat[:3,3]
        if exploded:xyz[:,2]+=shift(o)
        t=(xyz@M)[f];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
        lengths=np.linalg.norm(cross,axis=1);use=(lengths>1e-10)&(cross[:,2]<0)
        normals=cross[use]/lengths[use,None]
        illumination=.68+.34*np.maximum(0,normals@np.array([.35,.55,-.75]))
        rgb=np.array(o.LinkedObject.DisplayColour[:3])*255
        tris.append(t[use]);colors.append(np.clip(illumination[:,None]*rgb,0,255).astype('uint8'))
    ts=np.concatenate(tris);cs=np.concatenate(colors);lo=ts[:,:,:2].min(axis=(0,1));hi=ts[:,:,:2].max(axis=(0,1))
    W,H=1920,1080; margin=90
    scale=min((W-margin*2)/(hi-lo)[0],680/(hi-lo)[1])
    xy=np.rint((ts[:,:,:2]-(lo+hi)/2)*scale+[W/2,515]).astype('int32')
    im=Image.new('RGB',(W,H),'#f4f2e9');p=ImageDraw.Draw(im)
    p.rectangle((0,0,W,14),fill='#235a5c')
    p.text((86,48),'MERIDIAN   /   05',font=font(28,True),fill='#245d60')
    p.text((84,91),'Planet service sequence' if exploded else 'Single-stage planetary gearbox',font=font(61,True),fill='#172e36')
    for i in np.argsort(ts[:,:,2].mean(axis=1)):
        p.polygon([tuple(v) for v in xy[i]],fill=tuple(cs[i]))
    p.line((86,886,W-86,886),fill='#789495',width=2)
    if exploded:
        labels=[('01   CARTRIDGE','Remove six screws and pull the sun with its cover.'),('02   BRIDGE','Undo three flush screws and lift off the plate.'),('03   PLANETS','Remove clips and washers, then slide gears off pins.')]
    else:labels=[('INPUT','Integral sun shaft  /  18 teeth'),('FIXED RING','Three dog points lock the 72-tooth ring.'),('OUTPUT','Three planets drive the opposite-end carrier.')]
    for i,(title,line) in enumerate(labels):
        x=86+i*590;p.text((x,909),title,font=font(25,True),fill='#245d60');p.text((x,955),line,font=font(20),fill='#233b42')
    p.text((86,1024),'REFERENCE ASSEMBLY     /     5 : 1     /     MODULE 1',font=font(18),fill='#4c6369')
    im.save('Planet-service.png' if exploded else 'Assembly.png')
for mode in (False,True):drawplate(mode)
print('Rendered assembly and exploded service plates',len(physical),'components')

