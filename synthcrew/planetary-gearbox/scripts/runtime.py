"""Start the bundled FreeCAD Python runtime from the project directory."""
from pathlib import Path
import math
import os
import sys

prefix = Path(sys.executable).resolve().parents[1]
sys.path[:0] = [str(prefix / 'lib'), str(prefix / 'Mod' / 'PartDesign')]
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import FreeCAD as App
import Part
import Sketcher
from FreeCAD import Vector as V

App.ParamGet('User parameter:BaseApp/Preferences/Document').SetBool('RecoveryEnabled', False)
Gui=None
if os.environ.get('GEARBOX_GUI')=='1':
    import FreeCADGui as Gui
    Gui.showMainWindow()
    from PySide import QtCore, QtWidgets
    def dismiss_dialog():
        widget=QtWidgets.QApplication.activeModalWidget()
        if isinstance(widget,QtWidgets.QDialog):
            print('Closing unattended dialog',widget.windowTitle(),flush=True)
            widget.reject()
    dialog_timer=QtCore.QTimer()
    dialog_timer.timeout.connect(dismiss_dialog)
    dialog_timer.start(250)
App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles', 0)
App.ParamGet('User parameter:BaseApp/Preferences/Document').SetBool('SaveThumbnail', False)
MODEL = 'Planetary-Gearbox.FCStd'
def polar(r, a):
    return V(r*math.cos(math.radians(a)), r*math.sin(math.radians(a)), 0)
def pose(x=0,y=0,z=0,angle=0):
    return App.Placement(V(x,y,z),App.Rotation(V(0,0,1),angle))

