"""Preservation checkpoint, explicitly not a native parametric reconstruction."""
from sw_api import *
import json,sys,time
ROOT=Path(__file__).resolve().parents[2]
def run(part, mesh_brep=False, transport=False):
    s=attach();opts={CONST.swImportStlVrmlModelType:2,CONST.swImportStlVrmlUnits:CONST.swMM}
    toggles={CONST.swAlwaysUseDefaultTemplates:True,CONST.swVrmlStlImportAsPSMesh:mesh_brep}
    old={k:s.GetUserPreferenceIntegerValue(k) for k in opts}
    oldt={k:s.GetUserPreferenceToggle(k) for k in toggles}
    try:
        for k,v in opts.items():s.SetUserPreferenceIntegerValue(k,v)
        for k,v in toggles.items():s.SetUserPreferenceToggle(k,v)
        source=ROOT/'so101-mg996r/output/follower-r3/print-parts'/(part+'.stl')
        if transport:
            name=part.removesuffix('_MG996R_R3')
            proof=json.loads((ROOT/'solidworks/evidence'/(name+'_transport.json')).read_text())
            assert proof['status'].startswith('ACCEPTED'),proof
            source=ROOT/'solidworks/checkpoints/import_transport'/(part+'.stl')
        s.CloseDoc(part+'_REFERENCE.SLDPRT')
        print('Importing',source,flush=True)
        result=s.LoadFile4(str(source),'r',None,0)
        print('load result',result,flush=True)
        doc=model(result[0] if isinstance(result,tuple) else result)
        p=SW.IPartDoc(doc._oleobj_);bodies=p.GetBodies2(0,False)
        print('bodies',len(bodies or []),flush=True)
        evidence={'source':str(source),'body_count':len(bodies or []),'bodies':[],'mesh_brep_requested':mesh_brep}
        for b in bodies or []:
            b=SW.IBody2(b._oleobj_)
            evidence['bodies'].append({'box_m':list(b.GetBodyBox()),'mass_properties_density_1':list(b.GetMassProperties(1))})
        doc.ShowNamedView2('*Isometric',7);doc.ViewZoomtofit2()
        dest=ROOT/'solidworks/checkpoints/mesh_reference';dest.mkdir(exist_ok=True)
        path=dest/(part+'_REFERENCE.SLDPRT')
        status=doc.SaveAs3(str(path),0,1)
        evidence.update(save_error=status,path=str(path),native_features=False)
        (ROOT/'solidworks/evidence'/(part+'_import.json')).write_text(json.dumps(evidence,indent=2))
        print(json.dumps(evidence),flush=True)
    finally:
        for k,v in old.items():s.SetUserPreferenceIntegerValue(k,v)
        for k,v in oldt.items():s.SetUserPreferenceToggle(k,v)
if __name__=='__main__':run(sys.argv[1], '--mesh-brep' in sys.argv,'--transport' in sys.argv)
