"""README renders of actual exported meshes, never illustrative replacements."""
import json
from pathlib import Path
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from build_follower_r3 import worlds,matrix,WEB,ROOT

OUT=ROOT.parent/'docs/images';OUT.mkdir(parents=True,exist_ok=True)
m=json.loads((WEB/'study-manifest.json').read_text())
parts={p['id']:p for p in m['parts']};cache={}
def mesh(name):
    if name not in cache:cache[name]=trimesh.load(WEB/parts[name]['file'],force='mesh')
    return cache[name].copy()
def draw(ax,items,title,elev=24,azim=-64):
    points=[]
    light=np.array([-.3,-.6,.9]);light/=np.linalg.norm(light)
    for s,color in items:
        points.extend(s.bounds)
        shade=.5+.5*np.clip(s.face_normals@light,0,1)
        colors=np.array(to_rgb(color))[None,:]*shade[:,None]
        ax.add_collection3d(Poly3DCollection(s.triangles,facecolors=colors,linewidths=0,antialiased=False,rasterized=True))
    lo=np.min(points,axis=0);hi=np.max(points,axis=0);span=np.maximum(hi-lo,1);pad=span*.04
    ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1]);ax.set_zlim(lo[2]-pad[2],hi[2]+pad[2])
    ax.set_box_aspect(span);ax.set_proj_type('ortho');ax.view_init(elev,azim);ax.set_axis_off();ax.set_title(title,fontsize=13,pad=0)
def assembly(robot=None):
    w=worlds(m);items=[]
    for i in m['instances']:
        if robot and i['robot']!=robot:continue
        s=mesh(i['part']);s.apply_transform(w[i['node']]@matrix(i))
        color='#586472' if parts[i['part']]['kind']=='hardware' else '#5b8cdf' if i['robot']=='leader' else '#f0b943'
        items.append((s,color))
    return items
fig=plt.figure(figsize=(14,6),facecolor='#f4f6fa')
draw(fig.add_subplot(121,projection='3d'),assembly('follower'),'MG996R follower R3')
draw(fig.add_subplot(122,projection='3d'),assembly('leader'),'Passive AS5600 leader L1')
fig.suptitle('Original-derived CAD · nominal prototypes · physical testing pending',fontsize=14)
fig.savefig(OUT/'assembly.png',dpi=150,bbox_inches='tight');plt.close(fig)
fig=plt.figure(figsize=(9,7),facecolor='#f4f6fa');draw(fig.add_subplot(111,projection='3d'),assembly('leader'),'Original-derived SO-101 encoder leader · six passive joints')
fig.savefig(OUT/'leader.png',dpi=150,bbox_inches='tight');plt.close(fig)
offsets={'Encoder_cartridge_L1':0,'Encoder_rotor_L1':42,'Bearing_cap_front_L1':27,'688_bearing_front_L1':15,'688_bearing_rear_L1':-14,'Bearing_cap_rear_L1':-24,'Magnet_cup_L1':-37,'Diametric_magnet_L1':-48,'AS5600_PCB_L1':-64,'AS5600_chip_L1':-64,'AS5600_connectors_L1':-64}
items=[]
for name,z in offsets.items():
    s=mesh(name);s.apply_translation((0,0,z));color='#65a0e7' if parts[name]['kind']=='print' else '#238a73' if name.startswith('AS5600') else '#858e9a';items.append((s,color))
fig=plt.figure(figsize=(8,10),facecolor='#f4f6fa');draw(fig.add_subplot(111,projection='3d'),items,'Exploded encoder cartridge · two bearings / rotor / magnet / AS5600',20,-66)
fig.savefig(OUT/'encoder-exploded.png',dpi=140,bbox_inches='tight');plt.close(fig)
fig=plt.figure(figsize=(18,5),facecolor='#f4f6fa')
for k,p in enumerate(m['plates']):
    items=[]
    bed=trimesh.creation.box([256,256,1]);bed.apply_translation([128,128,-.6]);items.append((bed,'#dce2eb'))
    for e in p['entries']:
        s=mesh(e['part']);s.apply_transform(np.array(e['matrix']).reshape(4,4).T);items.append((s,'#5b8cdf' if p['robot']=='leader' else '#f0b943'))
    draw(fig.add_subplot(1,len(m['plates']),k+1,projection='3d'),items,p['label']+f"\n{p['count']} pieces",65,-90)
fig.suptitle('Five geometry-only P1S layouts · 256 × 256 mm beds · review slicing before printing',fontsize=15)
fig.savefig(OUT/'print-plates.png',dpi=130,bbox_inches='tight');plt.close(fig)
print('Rendered assembly, leader, cartridge and five plate views from actual meshes.')
