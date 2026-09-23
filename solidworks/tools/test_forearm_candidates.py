"""Import only disposable forearm candidates; never replace assembly references here."""
from sw_api import *
from native_hardware import typed
import json,sys
ROOT=Path(__file__).resolve().parents[2]
def main(name):
    s=attach();src=ROOT/'solidworks/checkpoints/import_transport'/(name+'.stl')
    old={k:s.GetUserPreferenceIntegerValue(k) for k in [CONST.swImportStlVrmlModelType,CONST.swImportStlVrmlUnits]}
    mesh=s.GetUserPreferenceToggle(CONST.swVrmlStlImportAsPSMesh)
    try:
        s.SetUserPreferenceIntegerValue(CONST.swImportStlVrmlModelType,2);s.SetUserPreferenceIntegerValue(CONST.swImportStlVrmlUnits,CONST.swMM);s.SetUserPreferenceToggle(CONST.swVrmlStlImportAsPSMesh,False)
        print('IMPORT',src,flush=True);d,e=s.LoadFile4(str(src),'r',None,0);assert d is not None,e
        doc=model(d);p=typed(doc,'IPartDoc')
        row={'candidate':name,'load_error':e,'solid_bodies':[],'surfaces':len(p.GetBodies2(1,False) or [])}
        for b in p.GetBodies2(0,False) or []:
            b=typed(b,'IBody2');row['solid_bodies'].append({'volume_mm3':b.GetMassProperties(1)[3]*1e9,'box_m':list(b.GetBodyBox()),'kernel_faults':b.Check2()})
        path=ROOT/'solidworks/checkpoints'/(name+'.SLDPRT');row['save_error']=doc.SaveAs3(str(path),0,1)
        (ROOT/'solidworks/evidence'/(name+'_import.json')).write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
    finally:
        for k,v in old.items():s.SetUserPreferenceIntegerValue(k,v)
        s.SetUserPreferenceToggle(CONST.swVrmlStlImportAsPSMesh,mesh)
if __name__=='__main__':main(sys.argv[1])
