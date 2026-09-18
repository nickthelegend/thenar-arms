"""Independently reload exported artifacts and check the bench test, not the arm."""
import json,hashlib,itertools,shutil
import cadquery as cq
import trimesh
import numpy as np
from build_fit_test import DEST,WEB
from clearance_study import servo

def main():
    report=json.loads((DEST/'verification.json').read_text())
    for p in report['parts']:
        path=DEST/p['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==p['sha256']
        mesh=trimesh.load(path,force='mesh')
        assert mesh.is_watertight and mesh.is_volume and len(mesh.split())==1,p['id']
        shape=cq.importers.importStep(str(DEST/p['step'])).val()
        assert shape.isValid() and len(shape.Solids())==1,p['id']
        assert abs(shape.Volume()-mesh.volume)/shape.Volume()<.002,p['id']
    fixture=cq.importers.importStep(str(DEST/report['parts'][0]['step'])).val()
    insertion=[]
    for z in np.linspace(0,60,13):
        volume=max(0,fixture.intersect(servo().translate((0,0,float(z)))).Volume())
        assert volume<.001,(z,volume)
        insertion.append({'lift_mm':float(z),'overlap_mm3':volume})
    for a,b in itertools.combinations(report['parts'],2):
        x=np.array(a['placed_bounds_mm']);y=np.array(b['placed_bounds_mm'])
        assert np.any(x[1,:2]<y[0,:2]) or np.any(y[1,:2]<x[0,:2]),(a['id'],b['id'])
    for name in ['P1S_FIT_TEST_ONLY','P1S_QUICK_GAUGES_ONLY']:
        scene=trimesh.load(DEST/(name+'.3mf'),force='scene')
        assert np.all(scene.bounds[0]>=[0,35,-.001]) and np.all(scene.bounds[1]<=[256,256,256])
        for m in scene.geometry.values():assert m.is_volume
        s=next(s for s in report['slicer']['plates'] if s['plate']==name)
        assert s['input_sha256']==hashlib.sha256((DEST/(name+'.3mf')).read_bytes()).hexdigest()
        assert s['exit_code']==0 and s['gcode_present']
    report['independent_export_check']={'passed':True,'method':'Reloaded STEP/STL/3MF, SHA256, one closed positive-volume shell per part, mesh/BREP volume within 0.2%, plate bounds and pairwise spacing, slicer input hashes, 13 nominal servo insertion heights. Not a strength or powered motion test.', 'insertion_samples':insertion}
    (DEST/'verification.json').write_text(json.dumps(report,indent=2));shutil.copy2(DEST/'verification.json',WEB/'fit-test/verification.json')
    print('PASS: 3 exported parts; 2 plate alternatives; 13 insertion samples; slicer input hashes match.')

if __name__=='__main__':main()
