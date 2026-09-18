"""Original SO101 leader + passive, two-bearing AS5600 cartridges (L1).

Uses the R3 original-mesh conversion operations with the leader's own source
instances and datums. The internal follower prefix is only the shared builder's
working namespace; publication changes it back to leader.
"""
import json, math, hashlib, xml.etree.ElementTree as ET
import numpy as np
import manifold3d as mf
import build_follower_r3 as b
from build_follower_r3 import box,cyl,union,transform,export,load,mesh,matrix,worlds

DEST=b.ROOT/'output/encoder-leader-l1'
WRIST_EXTENSION=14
UNITS={**dict(list(b.UNITS.items())[:5]),'Handle':['Wrist_Roll_SO101','Handle_SO101'],'Trigger':['Trigger_SO101']}
OWNERS=b.OWNERS[:5]+['Wrist_Roll_SO101']
DRIVEN=b.DRIVEN[:4]+['Wrist_Roll_SO101','Trigger_SO101']

def context():
    m=json.loads((b.ROOT/'output/manifest.json').read_text())
    m['nodes']=[n for n in m['nodes'] if n['id'].startswith('leader')]
    m['instances']=[i for i in m['instances'] if i['robot']=='leader' and i['part']!='WaveShare_Mounting_Plate_SO101']
    for n in m['nodes']:
        n['id']=n['id'].replace('leader','follower');n['parent']=n['parent'].replace('leader','follower') if n['parent'] else None
        if n['id']=='follower':n['position'][0]=0
        if n['id']=='follower_gripper_link_datum':n['position'][1]-=WRIST_EXTENSION
    for i in m['instances']:
        i['id']=i['id'].replace('leader','follower');i['node']=i['node'].replace('leader','follower');i['robot']='follower'
        if i['part']=='sts3215_03a_no_horn_v1':i['position'][1]-=WRIST_EXTENSION
        # The imported leader trigger pose was provisional. Its STEP mounting
        # face is local Z=6; register that face at output Z=16.7 mm.
        if i['part']=='Trigger_SO101':i['position'][2]=-4.0;i['rotation'][2]=15.0
    for i in m['nodes']+m['instances']:
        i['rotation']=[round(a/90)*90 if abs(a-round(a/90)*90)<.001 else a for a in i['rotation']]
    m['limits']=b.LIMITS;m['home']=[0,-25,35,0,0,20]
    w=worlds(m);ss=[i for i in m['instances'] if i['part'].startswith('sts3215')]
    ps={i['part']:i for i in m['instances'] if not i['part'].startswith('sts3215')}
    return m,ss,ps,[w[i['node']]@matrix(i) for i in ss],{p:w[i['node']]@matrix(i) for p,i in ps.items()}

def envelope(c=0,horn=False):
    return union([box((30.2+2*c,20.6+2*c,35.85+2*c),(12.5,0,-8.725)),
                  box((64+2*c,20+2*c,2.6+2*c),(5.05,0,-.4)),cyl(10+c,10.7-c,16.7)])

def mounting_passages():
    holes=[]
    for x in [-22.7,32.8]:
        for y in [-5,5]:holes.extend([cyl(1.7,-10,2,x,y),cyl(3.4,-14,-5.7,x,y)])
    holes.append(box((64.6,21.2,72),(5.05,0,34.6)))
    return union(holes)

def mounting_ledge():
    return box((74,29,4),(5.05,0,-3.7))-box((47.2,21.2,8),(4.6,0,-3.7))-mounting_passages()

def sweep(si,pi,j,m):
    t=b.relative_at(si,pi,j,0,m);r=np.linalg.inv(t)@b.relative_at(si,pi,j,10,m)
    sign=np.sign(math.atan2(r[1,0],r[0,0]));angles=np.linspace(*b.LIMITS[j],86)*sign
    solids=[]
    for length,width,x,z0,z1 in [(31,21.4,0,-27.05,9.6),(64.8,20.8,-7.45,-2.1,1.3),(74.6,29.6,-7.45,-6,-1.4)]:
        rect=mf.CrossSection.square((length,width),True).translate((x,0));copies=[rect.rotate(float(a)) for a in angles]
        swept=mf.CrossSection.batch_boolean([(a+c).hull() for a,c in zip(copies,copies[1:])],mf.OpType.Add).translate((12.5,0))
        solids.append(mf.Manifold.extrude(swept,z1-z0).translate((0,0,z0)))
    return transform(union(solids),t)

def cross_sweep(si,pi,j,m):
    from trimesh import transform_points
    pieces=[];ts=[b.relative_at(si,pi,j,float(a),m) for a in np.linspace(*b.LIMITS[j],33)]
    for solid in [box((31.2,21.6,36.85),(12.5,0,-8.725)),box((65,21,3.6),(5.05,0,-.4))]:
        points=mesh(solid).vertices;copies=[transform_points(points,t) for t in ts]
        pieces.extend(mf.Manifold.hull_points(np.vstack([a,c])) for a,c in zip(copies,copies[1:]))
    return union(pieces)

def hexagon(af,z0,z1,x=12.5,y=0):
    return mf.Manifold.cylinder(z1-z0,af/math.sqrt(3),circular_segments=6).rotate((0,0,30)).translate((x,y,z0))

def cartridge_parts():
    # Official Adafruit 6357 Eagle PCB, sensor-centred coordinates.
    tree=ET.parse(b.ROOT/'source/encoder/adafruit-as5600.brd')
    elems=tree.findall('.//board/elements/element')
    sensor=next(e for e in elems if e.get('value')=='AS5600')
    holes=[(float(e.get('x'))-float(sensor.get('x'))+12.5,float(e.get('y'))-float(sensor.get('y'))) for e in elems if e.get('value')=='MOUNTINGHOLE2.5']
    assert len(holes)==4
    frame=box((30.2,20.6,17.6),(12.5,0,-1.6))+box((30.2,20.6,1.5),(12.5,0,-25.9))
    for x in [-1.6,26.6]:frame+=box((2,20.6,14.75),(x,0,-17.775))
    for x,y in holes:
        frame+=cyl(2.4,-25.15,-24.15,x,y)
        frame-=cyl(.825,-26.7,-23.9,x,y) # M2 plastic screw pilot
        frame-=cyl(2.1,-12,9,x,y) # vertical driver access
    frame+=box((64,20,2.6),(5.05,0,-.4))
    for x in [-22.7,32.8]:
        for y in [-5,5]:frame-=cyl(1.7,-2,.95,x,y)
    frame-=cyl(4.3,-11,10)
    frame-=cyl(8.15,2.0,7.3);frame-=cyl(8.15,-10.5,-3)
    for x in [1.8,23.2]:
        frame-=cyl(.825,2,7.4,x,0);frame-=cyl(.825,-10.5,-4.5,x,0)
    # Cable portals for the QT connectors; soldered flexible leads also fit.
    for x in [-1.6,26.6]:frame-=box((3,6,5),(x,0,-21.65))
    cap=box((26,20,2),(12.5,0,8.2))-cyl(6.6,7.1,9.3)
    for x in [1.8,23.2]:cap-=cyl(1.1,7,10,x,0)
    rear=cap.translate((0,0,-19.6)) # -12.4..-10.4, below the frame
    rear+=cyl(8,-10.41,-8.2)-cyl(6.6,-10.5,-8.1) # 0.01 mm union overlap
    rotor=union([cyl(3.975,-8.15,7.15),cyl(5,7.15,10.7),cyl(10,10.7,16.7),hexagon(6.7,-10.15,-8.1)])
    rotor-=cyl(1.7,-11,17);rotor-=hexagon(5.7,14.1,17)
    for dx,dy in [(7,0),(-7,0),(0,7),(0,-7)]:
        rotor-=cyl(1.7,10,17,12.5+dx,dy)
        rotor-=hexagon(5.7,10.6,13.3,12.5+dx,dy)
    cup=cyl(5,-19.3,-8.15)-hexagon(7.0,-10.35,-8.0)-cyl(1.7,-16.3,-8)
    cup-=mf.Manifold.cylinder(1.5,3.2,1.7,circular_segments=128).translate((12.5,0,-16.2))
    cup-=cyl(3.1,-19.4,-16.8) # 6 x 2 diametric magnet, glue retained
    pcb=box((25.4,17.78,1.6),(12.5,0,-23.35))
    for x,y in holes:pcb-=cyl(1.25,-24.3,-22.4,x,y)
    chip=box((5,4,1.75),(12.5,0,-21.675))
    connectors=union([box((4.2,5,3),(12.5+dx,0,-21.05)) for dx in [-9.652,9.652]])
    bearing=cyl(8,2.1,7.1)-cyl(4,2,7.2)
    return {'Encoder_cartridge':(frame,'print',6),'Bearing_cap_front':(cap,'print',6),
            'Bearing_cap_rear':(rear,'print',6),'Encoder_rotor':(rotor,'print',6),
            'Magnet_cup':(cup,'print',6),'AS5600_PCB':(pcb,'hardware',6),
            'AS5600_chip':(chip,'hardware',6),'AS5600_connectors':(connectors,'hardware',6),
            '688_bearing_front':(bearing,'hardware',6),'688_bearing_rear':(bearing.translate((0,0,-10.2)),'hardware',6),
            'Diametric_magnet':(cyl(3,-18.8,-16.8),'hardware',6)},holes

def build_cartridge():
    parts,holes=cartridge_parts();rows=[]
    (DEST/'reference').mkdir(exist_ok=True)
    for name,(solid,kind,qty) in parts.items():
        row=export(solid,DEST/('print-parts' if kind=='print' else 'reference')/(name+'_L1.stl'))
        assert row['watertight'] and row['positive_volume']
        row.update(id=name+'_L1',label=name.replace('_',' '),kind=kind,quantity=qty)
        rows.append(row)
    report={'revision':'L1','parts':rows,'pcb_holes_xy_mm':holes,'pcb_source_sha256':hashlib.sha256((b.ROOT/'source/encoder/adafruit-as5600.brd').read_bytes()).hexdigest(),
            'pcb_mm':[25.4,17.78,1.6],'bearing':'688, 8 x 16 x 5 mm','magnet':'6 x 2 mm, diametrically magnetised',
            'magnet_chip_gap_mm':2.0,'physical_tested':False}
    (DEST/'encoder-build.json').write_text(json.dumps(report,indent=2))
    print('Encoder cartridge and original-derived leader generated',flush=True)

def finish_forearm(path):
    # The seam-fusion offset moves this ledge 0.029 mm into the cartridge tab.
    # Restore its seating plane with a 0.01 mm axial gap, without re-cutting all
    # coincident cavity faces. Independent attachment tests check the result.
    _,_,_,sm,pm=context()
    tool=transform(box((64.6,20.6,3),(5.05,0,-.21))+mounting_passages(),np.linalg.inv(pm['Under_arm_SO101'])@sm[3])
    return export(load(path)-tool,path)

def main():
    b.DEST=DEST;b.context=context;b.OWNERS=OWNERS;b.DRIVEN=DRIVEN;b.UNITS=UNITS
    b.servo=envelope;b.drive_keepout=sweep
    b.WRIST_EXTENSION_MM=WRIST_EXTENSION
    b.CASE_CLEARANCE_BOX=((30.8,21.2,36.45),(12.5,0,-8.725))
    b.TAB_HOLE_X=(-22.7,32.8);b.NUT_ACCESS_BOTTOM=-14
    b.flange_mount=mounting_ledge;b.slots=mounting_passages;b.cross_axis_keepout=cross_sweep
    b.REGISTRATION_OFFSETS={('Handle','Handle_SO101'):(.031,-.047,.029),('Forearm','Motor_holder_SO101_Wrist'):(.031,.003,.029)}
    # Both sources have already received the exact cavities/passages. The
    # translated handle lies outside the cartridge; avoid re-cutting coplanar
    # faces after their sub-0.1 mm seam fusion. Exported assembly is rechecked.
    b.SKIP_FUSED_RECUT={'Handle','Forearm','Wrist_pitch_roll','Upper_arm','Trigger'}
    b.main()
    report=json.loads((DEST/'build-report.json').read_text());m=json.loads((DEST/'assembly-source.json').read_text())
    names={}
    for p in report['print_units']:
        if p['id']=='Forearm_MG996R_R3':p.update(finish_forearm(DEST/'print-parts'/p['file']))
        old=p['file'];p['file']=old.replace('_MG996R_R3','_Encoder_L1');(DEST/'print-parts'/old).rename(DEST/'print-parts'/p['file'])
        names[p['id']]=p['id'].replace('_MG996R_R3','_Encoder_L1');p['id']=names[p['id']];p['label']=p['label'].replace('MG996R','encoder leader')
    for i in m['instances']:
        if i['part'] in names:i['part']=names[i['part']];i['id']=i['id'].replace('_MG996R_R3','_Encoder_L1')
    m['conversion_units']=report['print_units'];report['revision']='L1'
    report['status']='Passive encoder leader CAD; see verification report'
    report['pending']=['Physical bearing/journal fit','Magnet field and calibration test','Strength and cable routing']
    (DEST/'build-report.json').write_text(json.dumps(report,indent=2));(DEST/'assembly-source.json').write_text(json.dumps(m,indent=2))
    build_cartridge()

if __name__=='__main__':main()
