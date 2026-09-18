"""Package only explicitly approved test artifacts, never diagnostic meshes."""
import json,shutil,zipfile
from build_fit_test import ROOT,WEB,DEST

def main():
    report=json.loads((DEST/'verification.json').read_text())
    assert all(p['watertight'] and p['single_closed_shell'] for p in report['parts'])
    assert report['slicer_status']=='passed'
    selected=[p[key] for p in report['parts'] for key in ['file','step']]
    selected+=['P1S_FIT_TEST_ONLY.3mf','P1S_FIT_TEST_ONLY.stl','P1S_QUICK_GAUGES_ONLY.3mf',
               'BENCH_FIT_ASSEMBLY.step','MG996R_REFERENCE_DO_NOT_PRINT.stl','verification.json']
    for name in ['README.md','BOM.md','FIT-TEST.md']:shutil.copy2(ROOT/name,WEB/name)
    with zipfile.ZipFile(DEST/'MG996R-BENCH-FIT-R1.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in ['BOM.md','FIT-TEST.md']:z.write(ROOT/name,name)
        z.write(ROOT/'source/LICENSE','LICENSE-original-SO101.txt')
        for name in selected:z.write(DEST/name,name)
        for name in ['build_fit_test.py','slice_fit_test.py','verify_fit_test.py']:z.write(ROOT/'tools'/name,'tools/'+name)
        z.writestr('tools/REPRODUCING.txt','Run these tools from the thenar-arms workspace, not from this archive alone. They import the shared clearance/source helpers and pinned source STEP/manifest files. Python dependencies: cadquery, numpy, scipy, trimesh. Slicing requires the installed Bambu Studio P1S profiles. STL/STEP/3MF files themselves do not require these scripts.\n')
    shutil.copy2(DEST/'MG996R-BENCH-FIT-R1.zip',WEB/'fit-test/MG996R-BENCH-FIT-R1.zip')
    print('Packaged test parts, STEP, plates, checks, BOM and instructions; no unfinished arm or diagnostic meshes.')

if __name__=='__main__':main()
