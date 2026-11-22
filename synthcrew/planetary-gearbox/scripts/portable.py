"""Make file-property hints project-relative while keeping native embedded resources."""
from pathlib import Path
import re
import zipfile

def portable_model(filename):
    resources={'Template':'scripts/reference-frame.svg','FileGeomPattern':'scripts/section.pat','FileHatchPattern':'scripts/section-hatch.svg','NameGeomPattern':'Meridian'}
    dst=Path(filename).with_suffix('.staging')
    with zipfile.ZipFile(filename) as src,zipfile.ZipFile(dst,'w',compression=zipfile.ZIP_DEFLATED) as out:
        for entry in src.infolist():
            data=src.read(entry)
            if entry.filename=='Document.xml':
                for key,value in resources.items():
                    pattern=rb'(<Property name="'+key.encode()+rb'"[^>]*>\s*<String value=")[^"]*(")'
                    data=re.sub(pattern,lambda m:m[1]+value.encode()+m[2],data)
            elif entry.filename=='FCPAT.pat':data=Path('scripts/section.pat').read_bytes()
            elif entry.filename=='simple.svg':data=Path('scripts/section-hatch.svg').read_bytes()
            out.writestr(entry,data)
    dst.replace(filename)
if __name__=='__main__':portable_model('Planetary-Gearbox.FCStd')

