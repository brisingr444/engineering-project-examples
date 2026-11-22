"""Print native projected edges and measured dimensions to a portable vector PDF."""
from runtime import *
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch
import TechDraw

from print_geometry import print_document
d=print_document()
page=d.GeneralArrangement
# Restore the native HLR caches and section boundaries in this print session.
fig=plt.figure(figsize=(420/25.4,297/25.4))
ax=fig.add_axes([0,0,1,1],aspect='equal',xlim=(0,420),ylim=(0,297));ax.axis('off')
ink='#25383c';accent='#21595d'
def line(x1,y1,x2,y2,c=ink,lw=.53,ls='-'):
    ax.plot([x1,x2],[y1,y2],color=c,linewidth=lw,linestyle=ls)
def txt(x,y,s,size=8,**kw):
    ax.text(x,y,s,fontsize=size,color=kw.pop('color',ink),fontfamily='DejaVu Sans',**kw)
for x1,y1,x2,y2 in [(6,6,414,6),(6,291,414,291),(6,6,6,291),(414,6,414,291),(6,274,414,274),(6,23,414,23),(300,6,300,23)]:
    line(x1,y1,x2,y2,accent,.8)
txt(13,279,'MERIDIAN 05',17,weight='bold',color=accent)
txt(106,280,'SINGLE-STAGE PLANETARY GEARBOX',11)
txt(365,280,'GA  /  01',10)
txt(13,12,'GENERAL ARRANGEMENT    /    NOMINAL GEOMETRY',9)
txt(307,12,'mm    /    1:1 unless shown    /    A3',8)
def paths(view):
    k=view.Scale; x=view.X.Value;y=view.Y.Value
    coords=[]
    for i in range(len(view.getVisibleEdges())):
        ed=view.getEdgeByIndex(i)
        pts=ed.discretize(Deflection=.025)
        coords.append([(x+p.x*k,y+p.y*k) for p in pts])
    ax.add_collection(LineCollection(coords,colors=ink,linewidths=.54))
for view in [d.InputEnd,d.MeridianAA,d.HoleLayout]:paths(view)
# Shade actual intersections with the y=0 section plane. Align shaft extremities with their projected vertices.
sec=d.MeridianAA
verts=[sec.getVertexByIndex(i).Point for i in range(len(sec.getVisibleVertexes()))]
x0=d.MeridianAA.X.Value+min(p.x for p in verts)+47
ym=d.MeridianAA.Y.Value+(max(p.y for p in verts)+min(p.y for p in verts))/2
# y-axis in this view is +X (Y cross Z). Face polygons follow (z,x).
for o in sec.Source:
    for w in o.Shape.slice(V(0,1,0),0):
        if not w.isClosed():continue
        pts=w.discretize(Deflection=.04)
        xy=[(x0+p.z,ym+p.x) for p in pts]
        ax.add_patch(PathPatch(MplPath(xy+[xy[0]],[MplPath.MOVETO]+[MplPath.LINETO]*(len(xy)-1)+[MplPath.CLOSEPOLY]),facecolor='#e7eeee',edgecolor='#698284',linewidth=.21,hatch='////',zorder=.7))
def linear(dim):
    view=dim.References2D[0][0]
    refs=[s for obj,ss in dim.References2D for s in ss]
    pts=[view.getVertexByIndex(int(s.removeprefix('Vertex'))).Point for s in refs]
    px=[view.X.Value+p.x*view.Scale for p in pts];py=[view.Y.Value+p.y*view.Scale for p in pts]
    val=float(dim.getRawValue());lab=(dim.FormatSpec%val) if 'w' not in dim.FormatSpec else f'{val:g}'
    if dim.Type=='DistanceX':
        y=view.Y.Value+dim.Y.Value
        for x,yy in zip(px,py):line(x,yy,x,y+1,accent,.35)
        ax.annotate('',(min(px),y),(max(px),y),arrowprops=dict(arrowstyle='<->',color=accent,lw=.65,shrinkA=0,shrinkB=0))
        txt(sum(px)/2,y+1.5,lab,8,ha='center',color=accent)
    else:
        x=view.X.Value+dim.X.Value
        for xx,y in zip(px,py):line(xx,y,x+1,y,accent,.35)
        ax.annotate('',(x,min(py)),(x,max(py)),arrowprops=dict(arrowstyle='<->',color=accent,lw=.65,shrinkA=0,shrinkB=0))
        txt(x+1.6,sum(py)/2,lab,8,va='center',color=accent)
for n in ['CaseAxialLength','InputProjection','OutputProjection','InputJournalDiameter','OutputJournalDiameter']:linear(d.getObject(n))
v=d.HoleLayout
for n,angle,dx,dy in [('HousingDiameter',143,-41,29),('CoverBoltCircle',-32,39,-23),('PinCircle',57,22,26)]:
    dim=d.getObject(n);val=float(dim.getRawValue())
    r=val*v.Scale/2;theta=math.radians(angle);xy=(v.X.Value+r*math.cos(theta),v.Y.Value+r*math.sin(theta))
    ax.annotate(dim.FormatSpec%val,xy=xy,xytext=(v.X.Value+dx,v.Y.Value+dy),ha='right' if dx<0 else 'left',va='center',fontsize=8,color=accent,arrowprops=dict(arrowstyle='->',lw=.6,color=accent))
for o in page.Views:
    if o.TypeId=='TechDraw::DrawViewAnnotation':
        for i,s in enumerate(o.Text):txt(o.X.Value,o.Y.Value-i*6,s,10 if o==d.SetupNotes else 8,color=accent if i==0 else ink)
line(20,195,136,195,accent,.42,'-.');txt(15,196,'A',8);txt(137,196,'A',8)
fig.savefig('General-arrangement.pdf',metadata={'Title':'Meridian 05 | General arrangement','Author':'Meridian gearbox reference project'})
print('Printed',len(page.Views),'native sheet elements.',flush=True)

