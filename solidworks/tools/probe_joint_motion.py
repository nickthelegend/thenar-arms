from check_assembly_pose import *
import copy

def posed_worlds(m,q):
    w={}
    for n in m['nodes']:
        local=matrix(n)
        if n['joint'] is not None:
            r=np.eye(4);r[:3,:3]=Rotation.from_euler('z',q[n['joint']],degrees=True).as_matrix();local=local@r
        w[n['id']]=(w[n['parent']] if n['parent'] else np.eye(4))@local
    return w

def main():
    s,doc,asm,cs=connect();m=load_manifest();q=[0]*6;q[0]=15;w=posed_worlds(m,q)
    i=next(i for i in m['instances'] if i['part']=='Shoulder_MG996R_R3');c=cs[i['id']]
    print('before',c.GetConstrainedStatus(),flush=True)
    drag=typed(asm.GetDragOperator(),'IDragOperator');drag.AddComponent(c,False)
    drag.TransformType=2;drag.UseAbsoluteTransform=True;drag.ApplyToThisConfiguration=True
    print('begin',drag.BeginDrag(),flush=True)
    result=drag.Drag(sw_transform(s,w[i['node']]@matrix(i)))
    print('solver',result,'corrected',drag.DragCorrected,flush=True);drag.EndDrag()
    actual=from_sw(c);target=w[i['node']]@matrix(i)
    print('error',np.linalg.norm(actual[:3,3]-target[:3,3]),np.rad2deg(Rotation.from_matrix(target[:3,:3].T@actual[:3,:3]).magnitude()),flush=True)
    print('errors',[(n,f.GetErrorCode2()) for n,f in mate_features(doc).items()],flush=True)
    print('restore',c.SetTransformAndSolve3(sw_transform(s,worlds(m)[i['node']]@matrix(i)),True),flush=True)
    doc.ForceRebuild3(False)
if __name__=='__main__':main()
