"""Localized subtractive fit study on the ORIGINAL SO-101 BREP.

NOT a production conversion: mounting tabs, horn fasteners and opposite-side
support remain engineering release gates. Never silently repair detached solids.
"""
from pathlib import Path
import json, shutil, math, zipfile
import cadquery as cq
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from import_sources import ROOT, WEB, NAMES, tf, values

OUT=ROOT/'output/clearance-study'
for d in ['stl','step','reference']:(OUT/d).mkdir(parents=True,exist_ok=True)
(WEB/'clearance').mkdir(exist_ok=True)

def transform(s,m):
    r=Rotation.from_matrix(m[:3,:3]).as_rotvec();angle=np.linalg.norm(r)
    if angle>1e-9:s=s.rotate((0,0,0),tuple(r/angle),math.degrees(angle))
    return s.translate(tuple(m[:3,3]))
def matrix(item):
    m=np.eye(4);m[:3,:3]=Rotation.from_euler('XYZ',item['rotation'],degrees=True).as_matrix();m[:3,3]=item['position'];return m
def box(x,y,z,at):return cq.Workplane('XY').box(x,y,z,centered=(True,True,False)).translate(at).val()
def cylinder(r,h,at):return cq.Workplane('XY').circle(r).extrude(h).translate(at).val()
def servo(clearance=0):
    # Nominal MG996R case, with output axis registered to the STS3215 datum.
    # Published variants differ; these dimensions require caliper confirmation.
    c=clearance;bottom=-28.5;cx=2.05
    s=box(40.9+2*c,20+2*c,37+2*c,(cx,0,bottom-c))
    s=s.fuse(box(54+2*c,20+2*c,2.6+2*c,(cx,0,bottom+26.8-c)))
    s=s.fuse(cylinder(6.5+c,3+2*c,(12.5,0,bottom+37-c)))
    s=s.fuse(cylinder(3+c,8+2*c,(12.5,0,8.5-c)))
    # Purchased metal horn envelope. Spline detail is intentionally not fabricated.
    s=s.fuse(cylinder(10+c,4.5+2*c,(12.5,0,14.2-c)))
    if c:
        # Provisional straight connector/strain-relief clearance, not a bend simulation.
        s=s.fuse(box(12,9,9,(-24,0,bottom+3)))
    return s.clean()
def mesh_export(s,path):
    v,f=s.tessellate(.1,.15);m=trimesh.Trimesh([p.toTuple() for p in v],f,process=True)
    # Merge coincident BREP seam vertices at micron precision, never seal broad holes.
    m.merge_vertices(digits_vertex=6);m.update_faces(m.nondegenerate_faces())
    m.update_faces(m.unique_faces());m.remove_unreferenced_vertices()
    m.fix_normals();m.export(path)
    # Verify the actual float32 STL, not just the in-memory tessellation.
    return trimesh.load(path,force='mesh')

def main():
    manifest=json.loads((ROOT/'output/manifest.json').read_text())
    # Zero-joint transforms identify all six servos and every original part.
    world={}
    for n in manifest['nodes']:
        world[n['id']]=(world[n['parent']] if n['parent'] else np.eye(4))@matrix(n)
    instances=[i for i in manifest['instances'] if i['robot']=='follower']
    servos=[world[i['node']]@matrix(i) for i in instances if i['part'].startswith('sts3215')]
    prints={i['part']:world[i['node']]@matrix(i) for i in instances if i['part'] in NAMES}
    cavity=servo(.3);reference=servo(0)
    mesh_export(reference,OUT/'reference/MG996R_nominal_envelope.stl')
    shutil.copy2(OUT/'reference/MG996R_nominal_envelope.stl',WEB/'clearance/MG996R_nominal_envelope.stl')
    rows=[];drafts={}
    for n in NAMES:
        source=ROOT/'source/STEP'/(n+'.step')
        original=cq.importers.importStep(str(source)).val()
        solids=original.Solids();assert len(solids)==1,(n,len(solids));original=solids[0]
        edited=original;cuts=[]
        if n in prints:
            for index,sm in enumerate(servos):
                tool=transform(cavity,np.linalg.inv(prints[n])@sm)
                a=original.BoundingBox();b=tool.BoundingBox()
                if any(getattr(a,k+'max')<getattr(b,k+'min') or getattr(b,k+'max')<getattr(a,k+'min') for k in 'xyz'):continue
                overlap=original.intersect(tool).Volume()
                if overlap>.05:
                    cuts.append({'servo_index':index,'removed_intersection_mm3':round(overlap,3)})
                    edited=edited.cut(tool)
        edited=edited.clean();valid=edited.isValid();count=len(edited.Solids())
        removed=original.Volume()-edited.Volume()
        row={'part':n,'source_step':str(source.relative_to(ROOT)), 'intersections':cuts,'original_volume_mm3':round(original.Volume(),3),'removed_mm3':round(removed,3),'removed_percent':round(100*removed/original.Volume(),3),'valid_brep':valid,'solid_count':count,'status':'CLEARANCE ONLY — NOT PRINT RELEASE','attachment_verified':False,'wall_strength_verified':False,'physical_fit_verified':False}
        if valid and count==1:
            name=n+'_MG996R_clearance_DRAFT.stl'
            if removed>.05:
                mesh=mesh_export(edited,OUT/'stl'/name)
                cq.exporters.export(edited,str(OUT/'step'/(n+'_MG996R_clearance_DRAFT.step')))
            else:
                shutil.copy2(ROOT/'source/Individual'/(n+'.stl'),OUT/'stl'/name)
                mesh=trimesh.load(OUT/'stl'/name)
            row['draft_file']='stl/'+name;row['watertight']=bool(mesh.is_watertight)
            shutil.copy2(OUT/'stl'/name,WEB/'clearance'/name)
            if n in prints:drafts[n]={'file':'clearance/'+name,'bounds':mesh.extents.tolist(),'watertight':bool(mesh.is_watertight)}
        else:
            row['status']='REJECTED: clearance cut breaks or invalidates original part; no printable draft exported'
        rows.append(row);print(n, row['removed_percent'],'% removed;',count,'solids;',row['status'],flush=True)
    report={'status':'INCOMPLETE — nominal envelope study only; do not print as a finished conversion',
      'method':'Unscaled original STEP solids; localized subtraction around original servo datums. No replacement arm geometry.',
      'nominal_servo':{'body_mm':[40.9,20,37],'tab_span_mm':54,'tab_thickness_mm':2.6,'body_bottom_to_tab_mm':26.8,'clearance_per_side_mm':.3,'horn_envelope_diameter_mm':20,'horn_envelope_height_mm':4.5,'shaft_offset_from_case_end_mm':10,'source':'https://towerpro.com.tw/product/mg996R/','measured_hardware':False},
      'release_gates':['Confirm actual servo body, tab hole pitch, output shaft and supplied horn with calipers.','Design and validate mounting-tab fasteners and load paths.','Resolve MG996R single-output shaft versus stock passive-side support.','Validate wall thickness after clearance cuts, assembly access, cable routing and full swept collisions.','Evaluate direct-drive shoulder/elbow torque and heating; no payload is rated.','Design encoder cartridges in original leader housings after follower fit passes.','Slice only approved parts; then print a one-joint fit test before full plates.'],
      'parts':rows,'purchased_hardware':json.loads((ROOT/'purchased-hardware.json').read_text()),'leader_conversion':'Not attempted: original leader files preserved; no servo or encoder fit claim.'}
    (OUT/'fit-analysis.json').write_text(json.dumps(report,indent=2));shutil.copy2(OUT/'fit-analysis.json',WEB/'fit-analysis.json')
    # Optional study view replaces only follower geometry, preserving leader originals.
    study=json.loads(json.dumps(manifest));study['revision']='SO101-clearance-study';study['status']=report['status']
    preview=json.loads((ROOT/'preview-config.json').read_text())
    study['upstream_limits']=study['limits']
    study['limits']=preview['mg996r_limits_degrees'];study['home']=preview['home_degrees']
    study['limits_status']=preview['limits_status']
    for n,extra in drafts.items():
        p=next(p for p in study['parts'] if p['id']==n);p=dict(p)
        p.update(extra);p['id']=n+'_draft';p['label']=p['label']+' · clearance draft';p['notes']=report['status'];p['quantity']={'follower':1,'leader':0};study['parts'].append(p)
    ref=trimesh.load(OUT/'reference/MG996R_nominal_envelope.stl')
    study['parts'].append({'id':'MG996R_nominal','label':'MG996R nominal envelope','kind':'hardware','file':'clearance/MG996R_nominal_envelope.stl','bounds':ref.extents.tolist(),'watertight':bool(ref.is_watertight),'notes':'Nominal dimensions only. No detailed spline model.','quantity':{'follower':6,'leader':0}})
    for i in study['instances']:
        if i['robot']=='follower':
            if i['part'].startswith('sts3215'):i['part']='MG996R_nominal'
            elif i['part'] in drafts:i['part']+='_draft'
    for p in study['parts']:
        if p['kind']!='plate':
            p['quantity']={r:sum(i['part']==p['id'] and i['robot']==r for i in study['instances']) for r in ['follower','leader']}
    # Print plates intentionally remain original and labelled as such.
    (WEB/'study-manifest.json').write_text(json.dumps(study,indent=2))
    with zipfile.ZipFile(WEB/'MG996R-clearance-study-NOT-PRINT-RELEASE.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.write(ROOT/'README.md','READ-ME-FIRST.md')
        z.write(ROOT/'purchased-hardware.json','purchased-hardware.json')
        for p in OUT.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(OUT))
    print('Clearance study exported; release gates remain open.',flush=True)

if __name__=='__main__':main()
