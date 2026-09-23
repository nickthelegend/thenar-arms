"""Calculate mobility of the measured rigid-lock/hinge graph, separate from UI drag."""
from pathlib import Path
import numpy as np,json,sys
from prepare_follower_parts import load_manifest,worlds,matrix,ROOT
from leader_parts import manifest
from probe_joint_motion import posed_worlds
def skew(a):
    x,y,z=a;return np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
def main(robot):
    leader=robot=='leader';m=manifest() if leader else load_manifest();suffix='_Encoder_L1' if leader else '_MG996R_R3';name='leader_joint_motion_measurements.json' if leader else 'joint_motion_measurements.json';poses=json.loads((ROOT/'solidworks/evidence'/name).read_text());pose=next(p for p in poses if p['name']=='HOME');actual={r['id']:np.array(r['measured_transform_mm']) for r in pose['components']};instances=m['instances'];index={i['id']:k for k,i in enumerate(instances)};size=6*len(instances);constraints=[];rates=[];w=posed_worlds(m,pose['command_deg']);w0=worlds(m)
    def angular(p,c,axes):
        for axis in axes:
            row=np.zeros(size);row[index[c['id']]*6:index[c['id']]*6+3]=axis;row[index[p['id']]*6:index[p['id']]*6+3]=-axis;constraints.append(row)
    def point(p,c,at):
        mat=np.zeros((3,size))
        for i,sign in [(c,1),(p,-1)]:
            k=index[i['id']]*6;d=(at-actual[i['id']][:3,3])*.001;mat[:,k:k+3]=-sign*skew(d);mat[:,k+3:k+6]=sign*np.eye(3)
        constraints.extend(mat)
    base=next(i for i in instances if i['part']==('Base_Encoder_L1' if leader else 'Base_MG996R_R3'));ground=np.zeros((6,size));ground[:,index[base['id']]*6:index[base['id']]*6+6]=np.eye(6);constraints.extend(ground);locks=0
    for i in instances:
        if i['part'].endswith(suffix):continue
        owner=next(a for a in instances if a['node']==i['node'] and a['part'].endswith(suffix));angular(owner,i,np.eye(3));point(owner,i,actual[i['id']][:3,3]);locks+=1
    for n in m['nodes']:
        if n['joint'] is None:continue
        dat=next(a for a in m['nodes'] if a['id']==n['parent']);p=next(i for i in instances if i['node']==dat['parent'] and i['part'].endswith(suffix));c=next(i for i in instances if i['node']==n['id'] and i['part'].endswith(suffix))
        # Frame measured through the parent's actual CAD pose and its verified native datum.
        frame=actual[p['id']]@np.linalg.inv(w0[p['node']]@matrix(p))@w0[n['id']]
        point(p,c,frame[:3,3]);angular(p,c,[frame[:3,0],frame[:3,1]]);rate=np.zeros(size);rate[index[c['id']]*6:index[c['id']]*6+3]=frame[:3,2];rate[index[p['id']]*6:index[p['id']]*6+3]=-frame[:3,2];rates.append(rate)
    a=np.array(constraints);u,s,vh=np.linalg.svd(a,full_matrices=True);rank=int(sum(s>1e-8));null=vh[rank:].T;observability=np.array(rates)@null
    row={'classification':'CALCULATED from the native mate topology and CAD-measured HOME component frames; not a SolidWorks mouse-drag test or kernel DOF diagnostic','instances':len(instances),'grounded_components':1,'rigid_lock_mates':locks,'revolute_chains':6,'constraints_per_hinge':'Two angular + three joint-point coincidence constraints; source limit angles bound each remaining rotation','twist_variables':size,'constraint_rows':len(a),'rank':rank,'remaining_DOF':size-rank,'joint_rate_mapping_rank':int(np.linalg.matrix_rank(observability,tol=1e-8)),'nullspace_constraint_residual':float(np.max(abs(a@null))),'pass':size-rank==6 and np.linalg.matrix_rank(observability,tol=1e-8)==6,'scope':'Six independent rotational freedoms, with no additional infinitesimal freedoms in this graph at HOME. Actual native mate-driven movement is checked separately; free mouse dragging remains unverified.'}
    row['pass']=bool(row['pass']);(ROOT/'verification'/(robot+'_constraint_mobility.json')).write_text(json.dumps(row,indent=2));print(json.dumps(row,indent=2));assert row['pass']
if __name__=='__main__':main(sys.argv[1])
