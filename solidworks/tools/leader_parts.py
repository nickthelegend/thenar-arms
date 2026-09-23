"""Preserve L1 source geometry and add native articulation datums."""
from prepare_follower_parts import datum,worlds,ROOT,matrix
from native_hardware import *
import numpy as np,json,sys
def manifest():
    m=json.loads((ROOT/'robot-studio/public/models/so101/study-manifest.json').read_text())
    m['nodes']=[n for n in m['nodes'] if n['id'].startswith('leader')]
    m['instances']=[i for i in m['instances'] if i['robot']=='leader']
    m['nodes'][0]['position'][0]=0
    return m
def main(only=None):
    s=attach();m=manifest();w=worlds(m);out=ROOT/'solidworks/parts/leader';out.mkdir(parents=True,exist_ok=True)
    opts={CONST.swImportStlVrmlModelType:2,CONST.swImportStlVrmlUnits:CONST.swMM};tog={CONST.swAlwaysUseDefaultTemplates:True,CONST.swVrmlStlImportAsPSMesh:False}
    old={k:s.GetUserPreferenceIntegerValue(k) for k in opts};ot={k:s.GetUserPreferenceToggle(k) for k in tog}
    try:
        for k,v in opts.items():s.SetUserPreferenceIntegerValue(k,v)
        for k,v in tog.items():s.SetUserPreferenceToggle(k,v)
        for part in m['parts']:
            name=part['id']
            if not name.endswith('_Encoder_L1'):continue
            if only and only not in name:continue
            path=out/(name+'.SLDPRT');ev=ROOT/'solidworks/evidence'/(name+'_leader_part.json')
            if path.exists() and ev.exists():
                prior=json.loads(ev.read_text())
                if prior['solids'] and not prior['surface_bodies'] and all(b['kernel_faults']==0 for b in prior['solids']):print('Existing',name,flush=True);continue
                proof=ROOT/'solidworks/evidence'/(name+'_transport.json')
                assert proof.exists() and json.loads(proof.read_text())['accepted_transport'],('Prepare transport before retry',name)
                backup=ROOT/'solidworks/checkpoints/leader_failed_imports';backup.mkdir(exist_ok=True);shutil.copy2(path,backup/path.name);shutil.copy2(ev,backup/ev.name)
                s.CloseDoc(path.name)
            source=ROOT/'robot-studio/public/models/so101'/part['file']
            proof=ROOT/'solidworks/evidence'/(name+'_transport.json')
            if proof.exists() and json.loads(proof.read_text())['accepted_transport']:source=Path(json.loads(proof.read_text())['transport'])
            print('Import',name,flush=True)
            result=s.LoadFile4(str(source),'r',None,0);doc=model(result[0] if isinstance(result,tuple) else result);s.ActivateDoc3(doc.GetTitle(),False,0,0);p=typed(doc,'IPartDoc')
            bodies=p.GetBodies2(0,False) or [];before=[typed(b,'IBody2').Check2() for b in bodies]
            diagnosis=None
            if not bodies or any(before):diagnosis=p.ImportDiagnosis(True,False,True,0)
            inst=next(i for i in m['instances'] if i['part']==name);pworld=w[inst['node']]@matrix(inst);datums=[]
            for n in m['nodes']:
                if n['joint'] is None:continue
                fixed=next(a for a in m['nodes'] if a['id']==n['parent'])
                if inst['node'] not in [n['id'],fixed['parent']]:continue
                label='J'+str(n['joint']+1);t=np.linalg.inv(pworld)@w[n['id']];datum(doc,label,t);datums.append({'name':label,'matrix_mm':t.tolist()})
            doc.MaterialPropertyValues=com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,[.12,.40,.55,1,.5,.25,.1,0,0]);doc.ForceRebuild3(False)
            doc.ShowNamedView2('*Isometric',7);doc.ViewZoomtofit2();assert doc.SaveAs3(str(path),0,1)==0
            bodies=p.GetBodies2(0,False) or [];row={'part':name,'path':str(path),'source':str(source),'geometry':'Preserved imported L1 source, native joint datums; no recovered custom feature history','kernel_faults_before':before,'import_diagnosis_result':diagnosis,'solids':[{'kernel_faults':typed(b,'IBody2').Check2(),'box_m':list(typed(b,'IBody2').GetBodyBox()),'volume_m3':typed(b,'IBody2').GetMassProperties(1)[3]} for b in bodies],'surface_bodies':len(p.GetBodies2(1,False) or []),'datums':datums}
            ev.write_text(json.dumps(row,indent=2));print({k:v for k,v in row.items() if k not in ['datums','solids']},'body faults',[b['kernel_faults'] for b in row['solids']],flush=True);s.CloseDoc(doc.GetTitle())
    finally:
        for k,v in old.items():s.SetUserPreferenceIntegerValue(k,v)
        for k,v in ot.items():s.SetUserPreferenceToggle(k,v)
if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else None)
