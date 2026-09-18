"""Pack seven original-derived MG996R printing units, never stock SO101 plates."""
import json,itertools
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from rectpack import newPacker,MaxRectsBssf,MaxRectsBaf,MaxRectsBlsf,MaxRectsBl,SORT_AREA,SORT_PERI,SORT_LSIDE,SORT_SSIDE
from build_follower_r3 import DEST

ROTATIONS={'Base':[0,0,0],'Shoulder':[0,0,90],'Upper_arm':[90,0,0],
           'Forearm':[90,0,0],'Wrist_pitch_roll':[0,90,0],
           'Gripper_body':[0,90,0],'Moving_jaw':[0,90,0]}

def rotation(r):
    t=np.eye(4);t[:3,:3]=Rotation.from_euler('XYZ',r,degrees=True).as_matrix();return t

def main():
    units=json.loads((DEST/'build-report.json').read_text())['print_units']
    folder=DEST/'plates';folder.mkdir(exist_ok=True)
    meshes={};rotations={};choices={}
    for p in units:
        original=trimesh.load(DEST/'print-parts'/p['file'],force='mesh')
        assert original.is_volume and len(original.split())==1
        base=rotation(ROTATIONS[p['id'].removesuffix('_MG996R_R3')]);candidates=[]
        for flip in [0,180]:
            t=rotation([flip,0,0])@base;x=original.copy();x.apply_transform(t)
            h=x.triangles_center[:,2]-x.bounds[0,2]
            contact=float(x.area_faces[h<.05].sum())
            overhang=float(x.area_faces[(x.face_normals[:,2]<-.707)&(h>.4)].sum())
            candidates.append((-contact,overhang,t,x))
        contact,overhang,t,x=min(candidates,key=lambda v:v[:2])
        meshes[p['id']]=x;rotations[p['id']]=t
        choices[p['id']]={'bed_contact_area_mm2':-contact,'unsupported_down_face_area_mm2':overhang,
                          'orientation_method':'Original layout principal print axis, choosing the side with greatest flat bed contact; Bambu support generation still required.'}
    gap=12;packers=[]
    for algo,sort in itertools.product([MaxRectsBssf,MaxRectsBaf,MaxRectsBlsf,MaxRectsBl],[SORT_AREA,SORT_PERI,SORT_LSIDE,SORT_SSIDE]):
        packer=newPacker(pack_algo=algo,sort_algo=sort,rotation=True)
        for name,x in meshes.items():packer.add_rect(x.extents[0]+gap,x.extents[1]+gap,name)
        for _ in range(7):packer.add_bin(246,216)
        packer.pack()
        if len(packer.rect_list())==len(units):packers.append(packer)
    assert packers,'Packing failed'
    best=min(packers,key=lambda p:(len(p),sum(max(r.y+r.height for r in b) for b in p)))
    plates=[]
    for idx,bin in enumerate(best,1):
        scene=trimesh.Scene();entries=[];bounds=[]
        for rect in bin:
            name=rect.rid;x=meshes[name].copy();t=rotations[name].copy()
            if abs(rect.width-(x.extents[0]+gap))>.01:
                rz=rotation([0,0,90]);x.apply_transform(rz);t=rz@t
            offset=np.array([5+rect.x+gap/2,35+rect.y+gap/2,0])-x.bounds[0]
            x.apply_translation(offset);shift=np.eye(4);shift[:3,3]=offset;t=shift@t
            lo,hi=x.bounds
            assert np.all(lo>=[5,35,-.0001]) and np.all(hi<=[251,251,256]),(name,x.bounds)
            for a,b in bounds:assert any(hi[k]+gap-.01<=a[k] or b[k]+gap-.01<=lo[k] for k in [0,1])
            bounds.append(x.bounds);scene.add_geometry(x,node_name=name,geom_name=name)
            entries.append({'part':name,'matrix':t.T.ravel().tolist(),'bounds_mm':x.bounds.tolist()})
        name=f'P1S_MG996R_R3_{idx:02d}'
        scene.export(str(folder/(name+'.3mf')))
        plates.append({'id':name,'label':f'MG996R follower · plate {idx}','robot':'follower',
                       'prototype':True,'file':'follower-r3/plates/'+name+'.3mf','entries':entries,
                       'count':len(entries),'height':max(b[1,2] for b in bounds),
                       'bed_mm':[256,256],'part_spacing_mm':gap,'front_reserve_mm':35})
        print(name,len(entries),'parts',flush=True)
    report={'revision':'R3','plates':plates,'orientations':choices,
            'sliced':False,'globally_minimum_plate_count_proven':False,
            'method':'16 rectangle-packing candidates; 12 mm part spacing, 35 mm front reserve, 5 mm outer reserve. Counts exclude the obsolete stock WaveShare controller mount.'}
    (DEST/'plate-report.json').write_text(json.dumps(report,indent=2))

if __name__=='__main__':main()
