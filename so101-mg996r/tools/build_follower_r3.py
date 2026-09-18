"""Original-STL MG996R follower development, with explicit per-interface features.

Uses exact upstream meshes, not the rejected replacement arm. Manifold boolean
operations avoid the open tessellation seams of the previous OCC exports.
This is engineering development; the release decision comes from independent
checks, never from successful mesh export alone.
"""
from pathlib import Path
import hashlib, json, math
import numpy as np
import trimesh
import manifold3d as mf
from scipy.spatial.transform import Rotation
from clearance_study import ROOT, WEB, matrix

DEST = ROOT / 'output/follower-r3'
OWNERS = ['Base_motor_holder_SO101', 'Motor_holder_SO101_Base',
          'Upper_arm_SO101', 'Motor_holder_SO101_Wrist',
          'Wrist_Roll_Pitch_SO101', 'Wrist_Roll_Follower_SO101']
DRIVEN = ['Rotation_Pitch_SO101', 'Upper_arm_SO101', 'Under_arm_SO101',
          'Wrist_Roll_Pitch_SO101', 'Wrist_Roll_Follower_SO101', 'Moving_Jaw_SO101']
LIMITS = [[-85,85],[-80,80],[-80,80],[-80,80],[-85,85],[0,70]]
SEGMENTS = 128
REGISTRATION_OFFSETS = {}
SKIP_FUSED_RECUT = set()
WRIST_EXTENSION_MM = 8
CASE_CLEARANCE_BOX = ((41.5,20.6,37.6),(2.05,0,-10))
TAB_HOLE_X = (-22.7,26.8)
NUT_ACCESS_BOTTOM = None
UNITS={
    'Base': ['Base_SO101','Base_motor_holder_SO101'],
    'Shoulder': ['Rotation_Pitch_SO101','Motor_holder_SO101_Base'],
    'Upper_arm': ['Upper_arm_SO101'],
    'Forearm': ['Under_arm_SO101','Motor_holder_SO101_Wrist'],
    'Wrist_pitch_roll': ['Wrist_Roll_Pitch_SO101'],
    'Gripper_body': ['Wrist_Roll_Follower_SO101'],
    'Moving_jaw': ['Moving_Jaw_SO101'],
}

def union(shapes):
    return mf.Manifold.batch_boolean(list(shapes), mf.OpType.Add)

def box(size, centre):
    return mf.Manifold.cube(size, True).translate(centre)

def cyl(r, z0, z1, x=12.5, y=0):
    return mf.Manifold.cylinder(z1-z0, r, circular_segments=SEGMENTS).translate((x,y,z0))

def transform(shape, t):
    if np.allclose(t,np.eye(4),atol=1e-12,rtol=0):return shape
    return shape.transform(np.asarray(t)[:3,:])

def load(path):
    mesh=trimesh.load(path, force='mesh')
    assert mesh.is_watertight and mesh.is_volume, path
    shape=mf.Manifold(mf.Mesh64(np.asarray(mesh.vertices,dtype=np.float64),
                              np.asarray(mesh.faces,dtype=np.uint64)))
    assert shape.status()==mf.Error.NoError, (path,shape.status())
    return shape.set_tolerance(.005)

def mesh(shape):
    assert shape.status()==mf.Error.NoError,shape.status()
    raw=shape.to_mesh64()
    return trimesh.Trimesh(raw.vert_properties[:,:3],raw.tri_verts,process=False)

def export(shape,path):
    # Collapse sub-5-micron slivers BEFORE STL's float32 quantization. This is
    # bounded surface simplification, not hole filling or unconstrained repair.
    exact_volume=shape.volume()
    encoding='binary'
    for tolerance in [.005,.01,.02]:
        candidate=shape.as_original().set_tolerance(tolerance).simplify(tolerance)
        m=mesh(candidate); m.export(path)
        actual=trimesh.load(path,force='mesh')
        if actual.is_watertight and actual.is_volume:break
    if not actual.is_watertight:
        # Some exact CSG edges are distinct in double precision but coalesce in
        # binary STL's float32 coordinates. ASCII STL preserves those coordinates
        # without changing the geometry or guessing a mesh repair.
        binary_actual,binary_tolerance=actual,tolerance
        mesh(shape).export(path,file_type='stl_ascii')
        actual=trimesh.load(path,force='mesh');encoding='ASCII float64';tolerance=0
        if not actual.is_watertight:
            actual,tolerance=binary_actual,binary_tolerance;encoding='binary'
    repair=None
    if not actual.is_watertight:
        import pymeshfix
        fix=pymeshfix.MeshFix(actual.vertices,actual.faces)
        fix.repair(joincomp=False,remove_smallest_components=False)
        repaired=trimesh.Trimesh(fix.points,fix.faces,process=True)
        distances=[]
        for a,b in [(actual,repaired),(repaired,actual)]:
            points=trimesh.sample.sample_surface(a,10000,seed=101996)[0]
            distances.append(float(trimesh.proximity.closest_point(b,points)[1].max()))
        repair={'relative_volume_change':abs(repaired.volume-actual.volume)/actual.volume,
                'bounds_change_mm':float(np.max(abs(repaired.bounds-actual.bounds))),
                'bidirectional_sampled_surface_distance_mm':distances}
        assert repaired.is_watertight and repaired.is_volume and len(repaired.split())==1
        # Same 0.10 mm sampled deviation ceiling as the earlier repair study;
        # additionally require <0.01% volume change and unchanged outer bounds.
        assert repair['relative_volume_change']<.0001 and repair['bounds_change_mm']<.001 and max(distances)<.1,repair
        repaired.export(path);actual=trimesh.load(path,force='mesh')
    return {'file':path.name,'watertight':bool(actual.is_watertight),
            'positive_volume':bool(actual.is_volume),'shells':len(actual.split()),
            'bounds_mm':actual.bounds.tolist(),'volume_mm3':float(actual.volume),
            'surface_simplification_tolerance_mm':tolerance,
            'stl_encoding':encoding,
            'bounded_mesh_repair':repair,
            'relative_volume_change':abs(actual.volume-exact_volume)/exact_volume,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def servo(c=0, horn=True):
    # Body/tab datums match the earlier documented nominal MG996R envelope.
    items=[box((40.9+2*c,20+2*c,37+2*c),(2.05,0,-10)),
           box((54+2*c,20+2*c,2.6+2*c),(2.05,0,-.4)),
           cyl(6.5+c,8.5-c,11.5+c),cyl(3+c,8.5-c,14.2+c)]
    if horn:items.append(cyl(10+c,12.2-c,16.7+c))
    return union(items)

def metal_horn():
    # 42.7 mm shaft-tip height from the 37 mm case bottom: 5.7 mm above
    # the case. A 2 mm spline hub ends at that tip, beneath the 2.5 mm disc.
    h=union([cyl(5.5,12.2,14.2),cyl(10,14.2,16.7)])
    h-=cyl(2.75,11,18)
    for dx,dy in [(7,0),(-7,0),(0,7),(0,-7)]:h-=cyl(1.25,13,18,12.5+dx,dy)
    return h

def slots():
    holes=[]
    for x in TAB_HOLE_X:
        for y in [-5,5]:
            # 5 x 3.4 mm slots, with 1.6 mm centre travel along the tab span.
            holes.append(union([cyl(1.7,-8,2,x-.8,y),cyl(1.7,-8,2,x+.8,y),
                                box((1.6,3.4,10),(x,y,-3))]))
    return union(holes)

def flange_mount():
    ring=box((64,29,4),(2.05,0,-3.7))-box((41.5,20.6,8),(2.05,0,-3.7))
    return ring-slots()

def horn_plate():
    p=cyl(14,16.7,22.7)-cyl(3.2,16,24)
    for dx,dy in [(7,0),(-7,0),(0,7),(0,-7)]:p-=cyl(1.7,16,24,12.5+dx,dy)
    return p

def relative_at(tool_instance, part_instance, joint, angle, manifest):
    q=[0]*6;q[joint]=angle;w=worlds(manifest,q)
    return np.linalg.inv(w[part_instance['node']]@matrix(part_instance))@w[tool_instance['node']]@matrix(tool_instance)

def drive_keepout(tool_instance,part_instance,joint,manifest):
    """Conservative polygonal body/tab sweep about the output shaft.

    Adjacent 2-degree rectangular sections are convex-hulled before union;
    the maximum chord sagitta at 45 mm is 0.0069 mm. The 0.4 mm expansion
    includes this error plus the 0.3 mm intended running clearance.
    """
    t0=relative_at(tool_instance,part_instance,joint,0,manifest)
    r=np.linalg.inv(t0)@relative_at(tool_instance,part_instance,joint,10,manifest)
    assert abs(abs(r[2,2])-1)<1e-6
    sign=np.sign(math.atan2(r[1,0],r[0,0]))
    lo,hi=LIMITS[joint];angles=np.linspace(lo,hi,int(math.ceil((hi-lo)/2))+1)*sign
    solids=[]
    for length,width,z0,z1 in [(41.7,20.8,-28.9,8.9),(54.8,20.8,-2.1,1.3),
                               (64.6,29.6,-6,-1.4)]:
        rect=mf.CrossSection.square((length,width),True).translate((-10.45,0))
        copies=[rect.rotate(float(a)) for a in angles]
        steps=[(a+b).hull() for a,b in zip(copies,copies[1:])]
        sweep=mf.CrossSection.batch_boolean(steps,mf.OpType.Add).translate((12.5,0))
        solids.append(mf.Manifold.extrude(sweep,z1-z0).translate((0,0,z0)))
    solids.extend([cyl(6.9,8.1,11.9),cyl(3.4,8.1,14.6)])
    return transform(union(solids),t0)

def cross_axis_keepout(tool_instance,part_instance,joint,manifest):
    # A union of swept convex boxes for the roll motor crossing the pitch
    # holder. 0.5 mm padding exceeds the <0.1 mm 5-degree sagitta here.
    primitives=[box((41.9,21,38),(2.05,0,-10)),
                box((55,21,3.6),(2.05,0,-.4)),
                box((14,14,4),(12.5,0,10)),box((7,7,6.7),(12.5,0,11.35))]
    lo,hi=LIMITS[joint];angles=np.linspace(lo,hi,int(math.ceil((hi-lo)/5))+1)
    ts=[relative_at(tool_instance,part_instance,joint,float(a),manifest) for a in angles]
    pieces=[]
    for s in primitives:
        points=mesh(s).vertices
        moved=[trimesh.transform_points(points,t) for t in ts]
        pieces.extend(mf.Manifold.hull_points(np.vstack([a,b])) for a,b in zip(moved,moved[1:]))
    return union(pieces).as_original().simplify(.005)

def worlds(manifest,q=None):
    w={}
    for n in manifest['nodes']:
        t=matrix(n)
        if q is not None and n['joint'] is not None:
            r=np.eye(4);r[:3,:3]=Rotation.from_euler('z',q[n['joint']],degrees=True).as_matrix();t=t@r
        w[n['id']]=(w[n['parent']] if n['parent'] else np.eye(4))@t
    return w

def context():
    m=json.loads((ROOT/'output/manifest.json').read_text())
    # URDF/CAD export roundoff expresses right angles as e.g. 89.999702°.
    # Snap only rotations within 0.001° of a cardinal datum; retain the genuine
    # non-cardinal wrist offset. Max point shift is below 0.003 mm at 150 mm.
    for item in m['nodes']+m['instances']:
        item['rotation']=[round(a/90)*90 if abs(a-round(a/90)*90)<.001 else a for a in item['rotation']]
    m['limits']=LIMITS;m['home']=[0,-25,35,0,0,20]
    # The original, locally extended wrist moves both the roll motor and child
    # joint. Moving only the displayed servo would create a false assembly.
    for n in m['nodes']:
        if n['id']=='follower_gripper_link_datum':n['position'][1]-=8
    for i in m['instances']:
        if i['id']=='follower_sts3215_03a_no_horn_v1_12':i['position'][1]-=8
    w=worlds(m)
    inst=[i for i in m['instances'] if i['robot']=='follower']
    ss=[i for i in inst if i['part'].startswith('sts3215')]
    ps={i['part']:i for i in inst if not i['part'].startswith('sts3215')}
    sm=[w[i['node']]@matrix(i) for i in ss]
    pm={p:w[i['node']]@matrix(i) for p,i in ps.items()}
    return m,ss,ps,sm,pm

def main():
    DEST.mkdir(parents=True,exist_ok=True);(DEST/'parts').mkdir(exist_ok=True)
    m,ss,ps,sm,pm=context()
    original={p:load(ROOT/'source/Individual'/f'{p}.stl') for p in ps}
    shapes=dict(original)
    wrist=shapes['Wrist_Roll_Pitch_SO101']
    upper,lower=wrist.split_by_plane((0,0,1),18)
    bridge=mf.Manifold.extrude(wrist.slice(18),WRIST_EXTENSION_MM).translate((0,0,18-WRIST_EXTENSION_MM))
    shapes['Wrist_Roll_Pitch_SO101']=union([upper,lower.translate((0,0,-WRIST_EXTENSION_MM)),bridge])
    features={p:[] for p in ps}
    for j,p in enumerate(OWNERS):
        shapes[p]+=transform(flange_mount(),np.linalg.inv(pm[p])@sm[j])
        features[p].append({'feature':'4 mm MG996R tab ledge and four 5 x 3.4 mm slots','joint':j})
    for j,p in enumerate(DRIVEN):
        shapes[p]+=transform(horn_plate(),np.linalg.inv(pm[p])@sm[j])
        features[p].append({'feature':'20 mm metal horn interface, 14 mm PCD / four M3 holes','joint':j})
    # Remove fixed body envelopes from all source components. Keep exact flange
    # seating and horn mating planes, rather than floating both by the tolerance.
    fixed=servo(.3,False)
    fixed-=box((64,29,.3),(2.05,0,-1.85))
    fixed+=box(*CASE_CLEARANCE_BOX)
    for p in shapes:
        for j in range(6):
            tool=transform(fixed,np.linalg.inv(pm[p])@sm[j])
            shapes[p]-=tool
        # Nominal metal horn envelope is registered exactly against the plate.
        for j in range(6):
            shapes[p]-=transform(cyl(10.3,12.2,16.7),np.linalg.inv(pm[p])@sm[j])
    # Open the four screw passages in the original geometry too, not just in
    # the added mounting rings. Access holes are kept below the tab ledges.
    for j,p in enumerate(OWNERS):
        tool=slots()
        # Install the hornless servo from +Z before attaching the driven link.
        tool+=box((54.6,20.6,70),(2.05,0,33.6))
        for x in TAB_HOLE_X:
            for y in [-5,5]:tool+=cyl(3.4,-45 if NUT_ACCESS_BOTTOM is None else NUT_ACCESS_BOTTOM,-5.7,x,y)
        shapes[p]-=transform(tool,np.linalg.inv(pm[p])@sm[j])
    for j,p in enumerate(DRIVEN):
        tool=cyl(3.2,16.7,40)
        for dx,dy in [(7,0),(-7,0),(0,7),(0,-7)]:
            tool+=cyl(1.7,16.7,40,12.5+dx,dy)
            tool+=cyl(3.2,22.7,45,12.5+dx,dy)
        shapes[p]-=transform(tool,np.linalg.inv(pm[p])@sm[j])
        # Clearance around the moving horn flange in all fixed parent pieces.
        for fixed_part,inst in ps.items():
            if inst['node']==ss[j]['node']:
                shapes[fixed_part]-=transform(cyl(14.3,16.4,25.7),np.linalg.inv(pm[fixed_part])@sm[j])
    # Relief the moving fork cheeks across the specified joint travel, not just
    # at zero. This removes the incompatible stock STS rear-idler interface.
    # The resulting prototype is single-sided MG996R output support: no payload
    # or stiffness claim is inferred from a closed mesh.
    for j,p in enumerate(DRIVEN):
        shapes[p]-=drive_keepout(ss[j],ps[p],j,m)
        features[p].append({'feature':'Sampled moving MG996R body/tab relief; stock rear-idler pocket removed where intersecting','joint':j,'step_degrees':2})
        print('swept relief',p,flush=True)
    # The shifted roll motor can pass a pitch-mount tab at intermediate angles.
    shapes[OWNERS[3]]-=cross_axis_keepout(ss[4],ps[OWNERS[3]],3,m)
    # Fixed source pairs are fused into seven complete printing units below.
    # This removes reliance on threaded STS servo-case holes that the MG996R
    # does not have. Their original assembled geometry is preserved locally.
    # Re-cut fixed motor cavities after the mating recesses, then check exported
    # geometry independently. Do not suppress a remaining tab intersection.
    for p,inst in ps.items():
        for j,si in enumerate(ss):
            if si['node']==inst['node']:
                shapes[p]-=transform(fixed,np.linalg.inv(pm[p])@sm[j])
                if p!=OWNERS[j]:
                    # Only the actual holder needs a zero-gap tab seating face.
                    # Give other fixed pieces full tab underside clearance;
                    # this also avoids a coplanar hairline after STL quantizing.
                    shapes[p]-=transform(box((54.6,20.6,3.2),(2.05,0,-.4)),np.linalg.inv(pm[p])@sm[j])
                shapes[p]-=transform(box((54.6,20.6,70),(2.05,0,33.6)),np.linalg.inv(pm[p])@sm[j])
    rows=[]
    for p,s in shapes.items():
        shells=sorted(s.decompose(),key=lambda a:a.volume(),reverse=True)
        removed=[a.volume() for a in shells[1:] if a.volume()<30]
        kept=[a for a in shells if a.volume()>=30]
        s=union(kept);shapes[p]=s
        row=export(s,DEST/'parts'/f'{p}_MG996R_R3.stl')
        row.update({'part':p,'source_sha256':hashlib.sha256((ROOT/'source/Individual'/f'{p}.stl').read_bytes()).hexdigest(),
                    'features':features[p],'discarded_nonstructural_fragments_mm3':removed,
                    'structural_components':len(kept),'source_volume_mm3':original[p].volume(),
                    'removed_source_mm3':(original[p]-s).volume(),'added_mm3':(s-original[p]).volume()})
        rows.append(row);print(p,row['watertight'],row['structural_components'],round(row['added_mm3'],1),flush=True)
    export(servo(0,False),DEST/'MG996R_body_reference.stl')
    export(metal_horn(),DEST/'metal_horn_reference.stl')
    (DEST/'print-parts').mkdir(exist_ok=True)
    unit_rows=[];unit_instances=[]
    for name,members in UNITS.items():
        anchor=members[0]
        pieces=[];registration_overlap=[]
        for p in members:
            piece=transform(load(DEST/'parts'/f'{p}_MG996R_R3.stl'),np.linalg.inv(pm[anchor])@pm[p])
            if (name,p) in REGISTRATION_OFFSETS:
                delta=REGISTRATION_OFFSETS[name,p];piece=piece.translate(delta)
                registration_overlap.append({'source':p,'translation_mm':delta})
            if name=='Forearm' and p=='Motor_holder_SO101_Wrist':
                # A 50-micron overlap turns the original tangential seam into
                # a genuine fused interface. Re-test all shaft/tab/insertion
                # clearances on the joined part, including this tiny offset.
                piece=piece.translate((0,-.05,0))
                registration_overlap.append({'source':p,'translation_mm':[0,-.05,0]})
            if name=='Shoulder' and p=='Motor_holder_SO101_Base':
                piece=piece.translate((.031,-.047,.029))
                registration_overlap.append({'source':p,'translation_mm':[.031,-.047,.029]})
            pieces.append(piece)
        fused=union(pieces)
        for j,owner in enumerate(OWNERS):
            if owner not in members or name in SKIP_FUSED_RECUT:continue
            passage=slots()
            for x in TAB_HOLE_X:
                for y in [-5,5]:passage+=cyl(3.4,-80 if NUT_ACCESS_BOTTOM is None else NUT_ACCESS_BOTTOM,-5.7,x,y)
            fused-=transform(passage,np.linalg.inv(pm[anchor])@sm[j])
            fused-=transform(fixed,np.linalg.inv(pm[anchor])@sm[j])
        components=[c for c in fused.decompose() if c.volume()>1]
        assert len(components)==1,(name,'Unconnected fixed pieces',[(c.volume()) for c in components])
        row=export(fused,DEST/'print-parts'/f'{name}_MG996R_R3.stl')
        row.update({'id':name+'_MG996R_R3','label':name.replace('_',' ')+' · MG996R',
                    'source_parts':members,'anchor_source_frame':anchor,'registration_overlap':registration_overlap})
        unit_rows.append(row)
        instance=dict(ps[anchor]);instance['part']=row['id'];instance['id']='follower_'+row['id']
        unit_instances.append(instance)
        print('PRINT UNIT',name,row['watertight'],row['shells'],flush=True)
    m['instances']=[i for i in m['instances'] if i['robot']!='follower' or i['part'].startswith('sts3215')]+unit_instances
    m['conversion_units']=unit_rows
    report={'revision':'R3','status':'CAD prototype — consult separate interface, motion and slicing reports',
        'source':'Exact original SO101 individual meshes, locally modified; no whole-part scaling.',
        'wrist_axis_extension_mm':WRIST_EXTENSION_MM,'parts':rows,'print_units':unit_rows,'limits_degrees':LIMITS,
        'physical_fit_verified':False,'complete_arm_release':False,
        'pending':['Slicer/toolpath review','Physical nominal-fit test','Single-shaft load support and retention','Strength, powered operation and cable routing','Encoder leader conversion']}
    (DEST/'build-report.json').write_text(json.dumps(report,indent=2))
    (DEST/'assembly-source.json').write_text(json.dumps(m,indent=2))

if __name__=='__main__':main()
