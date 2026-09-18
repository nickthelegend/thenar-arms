"""One-servo bench fit prototype, derived from the original SO101 wrist holder.

This is NOT a full-arm release. Keep its manifest separate from the collision-
failing assembly. All tolerances and slotted hole positions are nominal until
the owner's purchased hardware has been measured and physically fitted.
"""
from pathlib import Path
import json, hashlib, shutil, zipfile
import cadquery as cq
import numpy as np
import trimesh
from clearance_study import ROOT, WEB, matrix, transform, servo, box, cylinder

DEST=ROOT/'output/fit-test-r1'

def export_mesh(shape,path):
    # STEP topology is the authority; merge only vertices closer than 1 micron.
    # OCC tessellation tolerances vary between curved/planar shared edges.
    for linear,angular,precision in [(.05,.08,6),(.03,.06,5),(.02,.04,4),(.05,.08,3)]:
        clean=shape.copy()
        vertices,faces=clean.tessellate(linear,angular)
        mesh=trimesh.Trimesh([v.toTuple() for v in vertices],faces,process=True)
        mesh.merge_vertices(digits_vertex=precision)
        mesh.update_faces(mesh.nondegenerate_faces());mesh.update_faces(mesh.unique_faces())
        mesh.remove_unreferenced_vertices();mesh.fix_normals()
        mesh.export(path)
        check=trimesh.load(path,force='mesh')
        if check.is_watertight and check.is_volume:
            return check,{'linear_mm':linear,'angular_rad':angular,'merge_digits':precision}
    raise ValueError(f'Non-watertight export: {path}')

def slot(x,y,z):
    return cq.Workplane('XY').center(x,y).slot2D(5.0,3.4,0).extrude(10).translate((0,0,z)).val()

def main():
    DEST.mkdir(parents=True,exist_ok=True);(WEB/'fit-test').mkdir(exist_ok=True)
    m=json.loads((ROOT/'output/manifest.json').read_text());world={}
    for n in m['nodes']:world[n['id']]=(world[n['parent']] if n['parent'] else np.eye(4))@matrix(n)
    inst=[i for i in m['instances'] if i['robot']=='follower']
    si=next(i for i in inst if i['id'].endswith('_11'))
    pi=next(i for i in inst if i['part']=='Motor_holder_SO101_Wrist')
    original_to_servo=np.linalg.inv(world[si['node']]@matrix(si))@world[pi['node']]@matrix(pi)
    source=ROOT/'source/STEP/Motor_holder_SO101_Wrist.step'
    original=cq.importers.importStep(str(source)).val().Solids()[0]
    original=transform(original,original_to_servo)

    # Existing rear holder plus local four-tab mounting ring. 4 mm ledges beneath
    # the tab bottom, no spline printed. Insertion from +Z with the horn REMOVED.
    ring=box(64,29,4,(2.05,0,-5.7)).cut(box(41.5,20.6,8,(2.05,0,-7.7)))
    cavity=servo(.3)
    # Preserve the exact tab seating plane instead of clearing 0.3 mm beneath
    # it (which would let the servo sink below the intended shaft datum).
    cavity=cavity.cut(box(64,29,.3,(2.05,0,-2)))
    cavity=cavity.fuse(box(41.5,20.6,37.6,(2.05,0,-28.8)))
    edited=original.fuse(ring).cut(cavity)
    insertion=box(54.6,20.6,65,(2.05,0,-1.4))
    edited=edited.cut(insertion).clean()
    holes=[(2.05+sx*24.75,sy*5) for sx in [-1,1] for sy in [-1,1]]
    for x,y in holes:
        edited=edited.cut(slot(x,y,-7.7))
        # A 6.8 mm underside access bore accepts an M3 nut (5.5 mm AF)
        # and provides a straight route from below. No blind buried nuts.
        edited=edited.cut(cylinder(3.4,39.3,(x,y,-45)))
    # Explicitly reject any severed structural body. The tiny original bottom
    # sliver has no load path after cavity subtraction and is deliberately removed.
    solids=sorted(edited.Solids(),key=lambda s:s.Volume(),reverse=True)
    fragments=[s.Volume() for s in solids[1:]]
    assert all(v<30 for v in fragments),('Detached structural material',fragments)
    edited=solids[0].clean()
    assert edited.isValid() and len(edited.Solids())==1
    fit_overlap=edited.intersect(servo()).Volume()
    assert fit_overlap<.001,fit_overlap
    insertion_overlap=edited.intersect(insertion).Volume()
    assert insertion_overlap<.001,insertion_overlap
    screw_access=[]
    for x,y in holes:
        bore=cylinder(3.4,39.3,(x,y,-45))
        value=edited.intersect(bore).Volume()
        assert value<.001,value
        screw_access.append(value)

    # A separate thin gauge checks body and both flange stations cheaply before
    # spending filament on a whole arm. It is a test tool, not replacement arm CAD.
    gauge=box(64,29,3,(2.05,0,0)).cut(box(41.5,20.6,5,(2.05,0,-1)))
    for x,y in holes:gauge=gauge.cut(slot(x,y,-1))
    # Two raised end strokes identify +X (output-shaft end), even without labels.
    gauge=gauge.fuse(box(1,2,1,(32.5,12,3))).fuse(box(1,2,1,(30.5,12,3))).clean()
    horn_gauge=cylinder(14,3,(0,0,0)).cut(cylinder(5.25,5,(0,0,-1)))
    for x,y in [(7,0),(-7,0),(0,7),(0,-7)]:
        horn_gauge=horn_gauge.cut(cylinder(1.7,5,(x,y,-1)))
    # Gauge checks a 20 mm, four-hole/14 mm PCD horn OPTION; no spline assumption.
    candidates=[('SO101_wrist_holder_MG996R_BENCH_ONLY',edited),
                ('MG996R_body_tab_gauge',gauge),('Horn_14mm_PCD_gauge',horn_gauge)]
    rows=[];objects=[]
    for index,(name,shape) in enumerate(candidates):
        assert shape.isValid() and len(shape.Solids())==1
        cq.exporters.export(shape,str(DEST/(name+'.step')))
        mesh,tess=export_mesh(shape,DEST/(name+'.stl'))
        native=mesh.copy()
        # Flat test gauges; original holder placed on its rear X face.
        rotation=np.eye(4)
        if index==0:
            rotation=trimesh.transformations.rotation_matrix(-np.pi/2,[0,1,0])
            mesh.apply_transform(rotation)
        xy=[(45,70),(120,70),(200,70)][index]
        offset=np.array([*xy,0])-mesh.bounds[0];mesh.apply_translation(offset)
        placement=np.eye(4);placement[:3,3]=offset;placement=placement@rotation
        assert np.all(mesh.bounds[0]>=[0,35,-.001]) and np.all(mesh.bounds[1]<=[256,256,256])
        objects.append((name,mesh))
        rows.append({'id':name,'file':name+'.stl','step':name+'.step','watertight':bool(native.is_watertight),
                     'single_closed_shell':len(native.split())==1,'valid_brep':shape.isValid(),
                     'bounds_mm':native.bounds.tolist(),'volume_mm3':float(native.volume),'tessellation':tess,
                     'sha256':hashlib.sha256((DEST/(name+'.stl')).read_bytes()).hexdigest(),
                     'placement_matrix':placement.T.reshape(-1).tolist(),'placed_bounds_mm':mesh.bounds.tolist()})
    scene=trimesh.Scene()
    for name,mesh in objects:scene.add_geometry(mesh,node_name=name,geom_name=name)
    scene.export(str(DEST/'P1S_FIT_TEST_ONLY.3mf'))
    trimesh.util.concatenate([mesh for _,mesh in objects]).export(DEST/'P1S_FIT_TEST_ONLY.stl')
    quick=trimesh.Scene()
    for name,mesh in objects[1:]:quick.add_geometry(mesh,node_name=name,geom_name=name)
    quick.export(str(DEST/'P1S_QUICK_GAUGES_ONLY.3mf'))
    # Servo and original-coordinate prototype are provided for CAD inspection.
    cq.exporters.export(transform(edited,np.linalg.inv(original_to_servo)),str(DEST/'wrist_holder_original_frame.step'))
    export_mesh(servo(),DEST/'MG996R_REFERENCE_DO_NOT_PRINT.stl')
    assembly=cq.Assembly();assembly.add(edited,name='bench_holder');assembly.add(servo(),name='nominal_servo')
    assembly.export(str(DEST/'BENCH_FIT_ASSEMBLY.step'))
    report={'status':'BENCH FIT PROTOTYPE ONLY — NOT A COMPLETE ARM',
        'original_source':'source/STEP/Motor_holder_SO101_Wrist.step','original_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'method':'Original wrist-holder BREP plus local tab ledges, 0.30 mm per-side body relief and top insertion opening. No arm replacement or mesh scaling.',
        'removed_disconnected_fragments_mm3':fragments,
        'nominal_case_mm':[40.9,20,37],'nominal_tab_span_mm':54,'tab_bottom_z_mm':-1.7,
        'cavity_mm':[41.5,20.6],'clearance_per_side_mm':.3,'support_ledge_thickness_mm':4,
        'slot_centres_mm':holes,'slot_total_length_mm':5,'slot_width_mm':3.4,
        'assumed_tab_pitch_mm':[49.5,10],'slot_pitch_is_measured':False,
        'nominal_servo_intersection_mm3':fit_overlap,'top_insertion_intersection_mm3':insertion_overlap,
        'underside_nut_access_diameter_mm':6.8,'nut_access_intersections_mm3':screw_access,
        'physical_fit_verified':False,'full_arm_collision_checked':False,'powered_motion_verified':False,
        'restrictions':['Unpowered bench fit only. Do not install this prototype into the full arm.',
                        'Original idle-side support and all original hardware interfaces remain unconverted.',
                        'Slot pitch, horn, wire strain relief and actual clone dimensions need physical checks.',
                        'The two wrist servos still clash in the full-arm study; this part does not fix that axis spacing.',
                        'No payload/strength/range certification; do not print the whole arm yet.'],
        'parts':rows,'plate_file':'P1S_FIT_TEST_ONLY.3mf','slicer_status':'not yet sliced'}
    (DEST/'verification.json').write_text(json.dumps(report,indent=2))
    deliverables=[r[key] for r in rows for key in ['file','step']]
    deliverables+=['P1S_FIT_TEST_ONLY.3mf','P1S_FIT_TEST_ONLY.stl','P1S_QUICK_GAUGES_ONLY.3mf',
                  'wrist_holder_original_frame.step','MG996R_REFERENCE_DO_NOT_PRINT.stl','BENCH_FIT_ASSEMBLY.step','verification.json']
    for name in deliverables:shutil.copy2(DEST/name,WEB/'fit-test'/name)
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':main()
