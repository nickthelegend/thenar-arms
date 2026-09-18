"""One reusable cartridge set, separate from the complete three-plate leader kit."""
import json,shutil
import numpy as np
import trimesh
from build_encoder_leader import DEST
from pack_encoder_leader import ROTATIONS
from pack_follower_r3 import rotation
import slice_follower_r3 as slicer

def main():
    target=DEST/'cartridge-fit';(target/'plates').mkdir(parents=True,exist_ok=True)
    rows=[p for p in json.loads((DEST/'encoder-build.json').read_text())['parts'] if p['kind']=='print']
    scene=trimesh.Scene();entries=[];x=15
    for p in rows:
        s=trimesh.load(DEST/'print-parts'/p['file'],force='mesh');t=rotation(ROTATIONS[p['id'].removesuffix('_L1')]);s.apply_transform(t)
        shift=np.array([x,45,0])-s.bounds[0];s.apply_translation(shift);t[:3,3]+=shift
        assert s.bounds[1,0]<251 and s.bounds[1,1]<251
        x=s.bounds[1,0]+12;scene.add_geometry(s,node_name=p['id'],geom_name=p['id'])
        entries.append({'part':p['id'],'matrix':t.T.ravel().tolist(),'bounds_mm':s.bounds.tolist()})
    name='P1S_ENCODER_CARTRIDGE_FIT';scene.export(str(target/'plates'/(name+'.3mf')))
    report={'plates':[{'id':name,'count':5,'entries':entries,'label':'One encoder cartridge · test first'}],'sliced':False}
    (target/'plate-report.json').write_text(json.dumps(report,indent=2));slicer.DEST=target;slicer.main()
    for e in entries:
        (target/'print-parts').mkdir(exist_ok=True);shutil.copy2(DEST/'print-parts'/(e['part']+'.stl'),target/'print-parts'/(e['part']+'.stl'))

if __name__=='__main__':main()
