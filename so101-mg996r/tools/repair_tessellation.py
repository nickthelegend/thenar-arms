"""Bounded mesh-seam repair. Never change CAD, bridge components or approve fit.

Uses PyMeshFix 0.18.1. Rejects repairs with >0.1 mm sampled surface change or
>0.1% volume difference from the STEP solid. Reports the comparison explicitly.
"""
import json,hashlib
import numpy as np
import trimesh
import pymeshfix
import cadquery as cq
from pathlib import Path

def repair(source,destination,step):
    before=trimesh.load(source,force='mesh');shape=cq.importers.importStep(str(step)).val()
    assert shape.isValid() and len(shape.Solids())==1
    fixer=pymeshfix.MeshFix(before.vertices,before.faces)
    fixer.repair(joincomp=False,remove_smallest_components=False)
    after=trimesh.Trimesh(fixer.points,fixer.faces,process=True)
    after.fix_normals()
    assert after.is_watertight and after.is_volume and len(after.split())==1
    assert np.max(np.abs(after.bounds-before.bounds))<.001
    relative_volume=abs(after.volume-shape.Volume())/shape.Volume()
    assert relative_volume<.001,relative_volume
    deviations=[]
    for a,b in [(before,after),(after,before)]:
        samples,_=trimesh.sample.sample_surface(a,10000,seed=101996)
        _,dist,_=trimesh.proximity.closest_point(b,samples)
        deviations.append(float(dist.max()))
    assert max(deviations)<.1,deviations
    after.export(destination)
    reloaded=trimesh.load(destination,force='mesh')
    assert reloaded.is_watertight and reloaded.is_volume
    report={'method':'PyMeshFix seam/degeneracy repair; join components OFF; remove smallest components OFF. STEP unchanged.',
        'source_sha256':hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        'repaired_sha256':hashlib.sha256(Path(destination).read_bytes()).hexdigest(),
        'before_faces':len(before.faces),'after_faces':len(after.faces),
        'watertight':bool(reloaded.is_watertight),'relative_volume_difference_from_step':relative_volume,
        'max_sampled_bidirectional_surface_deviation_mm':deviations,'samples_each_direction':10000,
        'mechanical_fit_certified':False}
    return report

if __name__=='__main__':
    import sys
    print(json.dumps(repair(*map(Path,sys.argv[1:4])),indent=2))
