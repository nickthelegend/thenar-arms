"""Refresh inspection downloads from current generated results; never touch originals."""
from pathlib import Path
import shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT.parent/'robot-studio/public/models/so101'
shutil.copy2(ROOT/'README.md',WEB/'README.md')
with zipfile.ZipFile(WEB/'SO101-originals.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.write(ROOT/'README.md','READ-ME-FIRST.md')
    for p in (ROOT/'source').rglob('*'):
        if p.is_file():z.write(p,p.relative_to(ROOT))
with zipfile.ZipFile(WEB/'MG996R-clearance-study-NOT-PRINT-RELEASE.zip','w',zipfile.ZIP_DEFLATED) as z:
    for file in ['README.md','purchased-hardware.json','preview-config.json','output/motion-verification.json']:
        z.write(ROOT/file,file)
    for p in (ROOT/'output/clearance-study').rglob('*'):
        if p.is_file():z.write(p,p.relative_to(ROOT/'output/clearance-study'))
    for p in (ROOT/'tools').glob('*.py'):z.write(p,p.relative_to(ROOT))
print('Updated source and inspection archives with current status and motion report.')
