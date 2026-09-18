"""Pack the complete leader quantity, including six of each cartridge piece."""
import json,itertools
import numpy as np
import trimesh
from rectpack import newPacker,MaxRectsBssf,MaxRectsBaf,MaxRectsBlsf,MaxRectsBl,SORT_AREA,SORT_PERI,SORT_LSIDE,SORT_SSIDE
from pack_follower_r3 import rotation
from build_encoder_leader import DEST

ROTATIONS={'Base':[0,0,0],'Shoulder':[0,0,90],'Upper_arm':[90,0,0],'Forearm':[90,0,0],
           'Wrist_pitch_roll':[0,90,0],'Handle':[0,90,0],'Trigger':[180,0,0],
           'Encoder_cartridge':[0,0,0],'Bearing_cap_front':[0,0,0],
           'Bearing_cap_rear':[0,0,0],'Encoder_rotor':[180,0,0],'Magnet_cup':[180,0,0]}

def main():
    build=json.loads((DEST/'build-report.json').read_text());enc=json.loads((DEST/'encoder-build.json').read_text())
    rows=build['print_units']+[p for p in enc['parts'] if p['kind']=='print'];meshes={};rotations={};instances={}
    for p in rows:
        name=p['id'];stem=name.replace('_Encoder_L1','').removesuffix('_L1')
        t=rotation(ROTATIONS[stem]);m=trimesh.load(DEST/'print-parts'/p['file'],force='mesh');assert m.is_volume and len(m.split())==1
        m.apply_transform(t);meshes[name]=m;rotations[name]=t
        for k in range(p.get('quantity',1)):instances[f'{name}_{k+1}']=name
    gap=12;candidates=[]
    for algo,sort in itertools.product([MaxRectsBssf,MaxRectsBaf,MaxRectsBlsf,MaxRectsBl],[SORT_AREA,SORT_PERI,SORT_LSIDE,SORT_SSIDE]):
        pk=newPacker(pack_algo=algo,sort_algo=sort,rotation=True)
        for key,name in instances.items():pk.add_rect(*(meshes[name].extents[:2]+gap),key)
        for _ in range(10):pk.add_bin(246,216)
        pk.pack()
        if len(pk.rect_list())==len(instances):candidates.append(pk)
    assert candidates
    best=min(candidates,key=lambda p:(len(p),sum(max(r.y+r.height for r in bin) for bin in p)))
    folder=DEST/'plates';folder.mkdir(exist_ok=True);plates=[]
    for idx,bin in enumerate(best,1):
        scene=trimesh.Scene();entries=[];bounds=[]
        for rect in bin:
            name=instances[rect.rid];x=meshes[name].copy();t=rotations[name].copy()
            if abs(rect.width-x.extents[0]-gap)>.01:r=rotation([0,0,90]);x.apply_transform(r);t=r@t
            shift=np.array([11+rect.x,41+rect.y,0])-x.bounds[0];x.apply_translation(shift);t[:3,3]+=shift
            lo,hi=x.bounds;assert np.all(lo>=[5,35,-.001]) and np.all(hi<=[251,251,256])
            for a,c in bounds:assert any(hi[k]+gap-.01<=a[k] or c[k]+gap-.01<=lo[k] for k in [0,1])
            bounds.append(x.bounds);scene.add_geometry(x,geom_name=rect.rid,node_name=rect.rid)
            entries.append({'part':name,'instance':rect.rid,'matrix':t.T.ravel().tolist(),'bounds_mm':x.bounds.tolist()})
        name=f'P1S_ENCODER_L1_{idx:02d}';scene.export(str(folder/(name+'.3mf')))
        plates.append({'id':name,'label':f'Encoder leader · plate {idx}','robot':'leader','prototype':True,
            'file':'encoder-leader-l1/plates/'+name+'.3mf','count':len(entries),'entries':entries,
            'height':max(v[1,2] for v in bounds),'part_spacing_mm':gap,'front_reserve_mm':35,'bed_mm':[256,256]})
    report={'revision':'L1','plates':plates,'part_count':len(instances),'unique_parts':len(rows),'sliced':False,
            'method':'16 packing candidates; explicit support-conscious print axes; 12 mm spacing; 35 mm front reserve. Not proven globally optimal.'}
    (DEST/'plate-report.json').write_text(json.dumps(report,indent=2));print(len(instances),'pieces on',len(plates),'P1S plates')

if __name__=='__main__':main()
