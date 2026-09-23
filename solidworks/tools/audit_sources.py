"""Read-only audit of original project; generated reports are kept separately."""
from pathlib import Path
import hashlib,json,re,csv,collections,zipfile
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'solidworks'
WEB=ROOT/'robot-studio/public/models/so101'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def matrix(item):
    t=np.eye(4);t[:3,:3]=Rotation.from_euler('XYZ',item['rotation'],degrees=True).as_matrix();t[:3,3]=item['position'];return t
def main():
    for d in ['parts','hardware','assemblies','exports','checkpoints','evidence']:(OUT/d).mkdir(parents=True,exist_ok=True)
    for d in ['docs','verification','simulation']:(ROOT/d).mkdir(exist_ok=True)
    inventory=[];terms=[];zip_entries=[]
    rx=re.compile(r'joint|axis|rotation|servo|MG996R|AS5600|angle|offset|limit|home|zero|\bmin\b|\bmax\b|gear|horn|link|length|transform|origin|position|quaternion|TODO|FIXME',re.I)
    for folder in [ROOT/'so101-mg996r',ROOT/'robot-studio',ROOT/'docs/images']:
        for p in sorted(folder.rglob('*')):
            if not p.is_file() or any(x in p.parts for x in ['node_modules','.git','__pycache__']):continue
            row={'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p),'extension':p.suffix.lower()}
            inventory.append(row)
            if p.suffix.lower() in ['.py','.js','.mjs','.ts','.json','.md','.h','.cpp','.ino','.urdf','.brd','.txt','.svg','.dxf']:
                txt=p.read_text(encoding='utf-8',errors='replace')
                for num,line in enumerate(txt.splitlines(),1):
                    if rx.search(line):terms.append({'file':row['path'],'line':num,'text':line})
            if p.suffix.lower() in ['.zip','.3mf']:
                with zipfile.ZipFile(p) as z:zip_entries.append({'path':row['path'],'entries':z.namelist()})
    (OUT/'checkpoints/original_files_sha256.json').write_text(json.dumps(inventory,indent=2))
    (ROOT/'verification/source_text_index.json').write_text(json.dumps(terms,indent=2))
    (ROOT/'verification/archive_contents.json').write_text(json.dumps(zip_entries,indent=2))
    manifest=json.loads((WEB/'study-manifest.json').read_text())
    selected=[]
    for p in manifest['parts']:
        if not any(i['part']==p['id'] for i in manifest['instances']):continue
        f=WEB/p['file'];m=trimesh.load(f,force='mesh')
        selected.append({'id':p['id'],'source':f.relative_to(ROOT).as_posix(),'sha256':digest(f),'triangles':len(m.faces),'watertight':bool(m.is_watertight),'volume_mm3':float(m.volume),'bounds_mm':m.bounds.tolist()})
    (ROOT/'verification/source_geometry.json').write_text(json.dumps(selected,indent=2))
    joints=[]
    names=['shoulder_pan','shoulder_lift','elbow_flex','wrist_flex','wrist_roll','gripper']
    for n in manifest['nodes']:
        if not n['id'].startswith('follower') or n['joint'] is None:continue
        j=n['joint'];datum=next(x for x in manifest['nodes'] if x['id']==n['parent'])
        origin=matrix(datum);rpy=Rotation.from_matrix(origin[:3,:3]).as_euler('xyz').tolist()
        joints.append({'joint_name':names[j],'parent_link':datum['parent'].removeprefix('follower_'),'child_link':n['id'].removeprefix('follower_'),'joint_type':'revolute','origin_xyz_m':(origin[:3,3]/1000).tolist(),'origin_rpy_rad':rpy,'axis':[0,0,1],'positive_direction':'right-hand rule about local +Z','mechanical_zero':'manifest q=0; physical horn indexing UNVERIFIED','software_zero_degrees':0,'home_degrees':manifest['home'][j],'minimum_degrees':manifest['limits'][j][0],'maximum_degrees':manifest['limits'][j][1],'limits_status':'SOURCE VERIFIED software/preview limits; mechanical collision-free range UNVERIFIED','servo_channel':j,'MG996R_identifier':f'MG996R_{j+1}','servo_sign':1,'servo_sign_status':'source default, physical direction UNVERIFIED','servo_zero_us':1500,'us_per_degree':5.555556,'gear_ratio':1,'firmware_variable':f'current[{j}], goal[{j}], SERVO_SIGN[{j}], SERVO_ZERO_US[{j}]','solidworks_components':[i['id'] for i in manifest['instances'] if i['robot']=='follower' and i['node'] in [n['id'],datum['parent']]],'evidence':'study-manifest.json; build_follower_r3.py; firmware/thenar/model.h; calibration.h'})
    import yaml
    (ROOT/'simulation/joint_map.yaml').write_text(yaml.safe_dump({'status':'SOURCE VERIFIED kinematic inputs; SolidWorks verification pending','units':'SI except explicitly suffixed values','joints':joints},sort_keys=False))
    (ROOT/'docs/source_audit.md').write_text('''# Reconstruction source audit

Current target: SO101-MG996R follower R3 and passive AS5600 leader L1. Engineering prototypes, not physically tested or payload rated.

## Authority and revision

No original parametric CAD, SLDPRT, SLDASM or FCStd is present in the supplied project. Fourteen upstream STEP solids exist, but these are the STOCK geometry. The current R3/L1 modifications were performed on the upstream STL meshes with manifold3d, not on those STEP solids. Substituting stock STEP geometry would discard current mounts, travel reliefs, seam overlaps and wrist extensions. The R3/L1 generator code plus its hash-identified released meshes and assembly transforms are the authority for the CURRENT revisions. Historical R1/R2/clearance STEP files are not current R3 parts. No geometry averaging is permitted.

The audit inventories and hashes every original file, reads text sources into a searchable line index, inventories ZIP/3MF contents, and measures every used published mesh. Binary source files are preserved. These checks do not establish native feature reconstruction or physical fit. See verification/source_geometry.json and solidworks/checkpoints/original_files_sha256.json.

## Dimensional register

| Quantity | Value | Units | Source | Classification / conflicts |
|---|---|---|---|---|
| MG996R case | 40.9 × 20 × 37 | mm | R3-PRINT.md; build_follower_r3.servo | SOURCE VERIFIED nominal input; purchased hardware unmeasured |
| Case bottom / top | -28.5 / 8.5 | mm local servo Z | build_follower_r3.servo | SOURCE VERIFIED |
| Shaft centre | 12.5, 0 | mm local servo XY | build_follower_r3.cyl | SOURCE VERIFIED |
| Shaft tip | 14.2 | mm local servo Z | build_follower_r3.servo | SOURCE VERIFIED; historical clearance model differs |
| Tab span / width / thickness | 54 / 20 / 2.6 | mm | build_follower_r3.servo | SOURCE VERIFIED nominal |
| Tab holes / slots | 49.5 × 10 / 5 × 3.4 | mm | R3-PRINT.md; slots() | SOURCE VERIFIED nominal |
| Metal disc / hole PCD | 20 / 14 | mm | metal_horn() | SOURCE VERIFIED option, actual horn UNVERIFIED |
| Metal-disc holes | 2.5 | mm | metal_horn() | SOURCE VERIFIED tap-drill envelope; M3 threads unmodelled |
| Printed horn holes / centre bore | 3.4 / 6.4 | mm | horn_plate() | SOURCE VERIFIED |
| Horn stack / driven plate | 4.5 / 6 | mm | metal_horn(); horn_plate() | SOURCE VERIFIED |
| Follower wrist extension | 8 | mm | R3 generator + manifests | SOURCE VERIFIED; do not use stock/R2 geometry |
| Leader wrist extension | 14 | mm | L1 generator | SOURCE VERIFIED; differs deliberately from follower |
| Shoulder seam overlap | 0.031, -0.047, 0.029 | mm | R3 generator | SOURCE VERIFIED local translation |
| Follower forearm seam overlap | 0, -0.05, 0 | mm | R3 generator | SOURCE VERIFIED local translation |
| Adafruit6357 board | 25.4 × 17.78 × 1.6 | mm | Eagle + L1 source | Outline SOURCE VERIFIED; thickness ASSUMED in source |
| PCB holes | ±10.16 × ±6.35; diameter 2.5 | mm | Eagle + L1 source | SOURCE VERIFIED |
| Bearings | 8 × 16 × 5 | mm | ENCODER-LEADER.md; L1 source | SOURCE VERIFIED nominal 688ZZ |
| Bearing pocket / journal | 16.3 / 7.95 | mm | cartridge_parts() | SOURCE VERIFIED |
| Magnet / pocket | diameter 6 × 2 / diameter 6.2 | mm | cartridge_parts() | SOURCE VERIFIED nominal |
| Magnet-to-chip gap | 2 | mm | L1 report + source | SOURCE VERIFIED nominal; field strength UNVERIFIED |
| Leader trigger indexing | +15 | deg | L1 context() | SOURCE VERIFIED revision correction |
| Follower joint origins | six complete matrices | mm / degrees | published manifest | SOURCE VERIFIED; copied to simulation/joint_map.yaml in SI |
| Home | 0, -25, 35, 0, 0, 20 | deg | model.h + manifest | SOURCE VERIFIED; differs from ZERO |
| Preview/command limits | ±85, ±80, ±80, ±80, ±85, 0–70 | deg | model.h + manifest | SOURCE VERIFIED software limits, NOT physical travel certification |
| Direct drive ratio | 1:1 | ratio | model.h + R3 guide | SOURCE VERIFIED; historical custom-arm 2:1 is excluded |
| Display base separation | 800 | mm | publisher/viewer | Display only; remove ±400 mm X shifts for separate robot assemblies |

## Coordinates and mechanism

Source position values are millimetres; source rotations use intrinsic XYZ Euler degrees (Three.js XYZ). Each fixed joint datum is followed by an independent local Z rotation. Converting these rotations to URDF requires matrix conversion to extrinsic xyz RPY radians, not copying the Euler triples. Native SolidWorks assembly convention will retain source world axes with Z up. Separate assemblies remove only viewer root X offsets; the 2.4 mm vertical root placement is explicit. ROS base_link convention retains original URDF frame and needs an explicit ground offset of 2.4 mm when used with a table.

The sixth follower actuator rotates one moving jaw directly; the opposite gripping surface is part of Gripper_body. There is no evidence of a paired-jaw linkage, gear reduction, or parallel-jaw translation. Horns belong to child links, servo bodies to parent links. Leader rotor, magnet cup and magnet belong to child links; cartridge, caps, boards and bearing envelopes belong to parent links.

## Conflicts and unknowns

The original URDF includes STS3215 mass/inertia and limits. They cannot be reused for the modified MG996R/PETG robot. Physical servo signs, horn indexing, travel and pulse slopes are uncalibrated defaults. Materials/infill and purchased component masses do not establish assembled mass/inertia. Keep unknown dynamics UNVERIFIED.

Existing follower report: 72 discrete poses internally clear at its 0.5 mm³ threshold, eight table-intersection poses. Existing leader report: two folded internal collisions, eleven table-intersection poses. These are inherited source reports, not new SolidWorks tests, and they do not certify swept motion. Preserve known collisions without redesigning geometry.
''',encoding='utf-8')
    (ROOT/'docs/decision_log.md').write_text('''# Reconstruction decisions

- Preserve R3 and L1 as distinct current revisions. Original inputs are hash-checkpointed and remain untouched.
- SolidWorks 2026 SP4.1 is open and reachable through the installed COM API. No SolidWorks MCP tool/server is configured in this task. Use the user-authorized API fallback and record it explicitly.
- Do not overwrite or close the user's SolidWorks_Test_Plate document.
- Exact current meshes are the baseline comparison, with native reconstruction to be accepted only after numerical comparison. Imported references alone do not satisfy native parametric reconstruction.
- Do not inherit stock URDF dynamics or pretend uncalibrated physical limits are verified. Source software limits and physical collision results remain separately labelled.
''',encoding='utf-8')
    (ROOT/'docs/open_issues.md').write_text('''# Open issues

- Native R3/L1 feature reconstruction, articulated assemblies and SolidWorks motion checks are pending.
- Current custom geometry is mesh-derived; source STEP is a different revision. A feature reconstruction must be checked against R3/L1 meshes.
- The joint limits are provisional software limits, and some combined poses hit the table. Physical mechanical endpoints are unknown.
- Source mass/inertia for the MG996R conversion is absent. Printed infill, fastener geometry, actual servo mass/COM and hardware calibration need evidence.
- Isaac Sim and ROS availability have not yet been established. No simulator readiness claim is made.
''',encoding='utf-8')
    (ROOT/'docs/progress.md').write_text('# Progress\n\nSource inventory, source text index, revision audit and initial joint mapping created. SolidWorks COM attachment verified. Geometry reconstruction and downstream verification are in progress; no completion claim.\n',encoding='utf-8')
    print(json.dumps({'files':len(inventory),'text_matches':len(terms),'archives':len(zip_entries),'used_meshes':len(selected),'joints':len(joints),'extensions':dict(collections.Counter(x['extension'] for x in inventory))}))
if __name__=='__main__':main()
