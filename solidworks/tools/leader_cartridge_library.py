"""Native practical L1 caps and envelopes, preserved source for complex cartridge prints."""
from leader_parts import *
def main():
    s=attach();m=manifest();out=ROOT/'solidworks/hardware/leader';out.mkdir(parents=True,exist_ok=True)
    holes=json.loads((ROOT/'so101-mg996r/output/encoder-leader-l1/encoder-build.json').read_text())['pcb_holes_xy_mm']
    imported={'Encoder_cartridge_L1','Encoder_rotor_L1','Magnet_cup_L1'}
    for part in m['parts']:
        name=part['id']
        if not name.endswith('_L1') or name.endswith('_Encoder_L1'):continue
        path=out/(name+'.SLDPRT');ev=ROOT/'solidworks/evidence'/(name+'_leader_part.json')
        if path.exists() and ev.exists():print('Existing',name,flush=True);continue
        print('Build',name,flush=True)
        if name in imported:
            source=ROOT/'robot-studio/public/models/so101'/part['file']
            oldi={k:s.GetUserPreferenceIntegerValue(k) for k in [CONST.swImportStlVrmlModelType,CONST.swImportStlVrmlUnits]};oldb=s.GetUserPreferenceToggle(CONST.swVrmlStlImportAsPSMesh)
            try:
                s.SetUserPreferenceIntegerValue(CONST.swImportStlVrmlModelType,2);s.SetUserPreferenceIntegerValue(CONST.swImportStlVrmlUnits,CONST.swMM);s.SetUserPreferenceToggle(CONST.swVrmlStlImportAsPSMesh,False)
                res=s.LoadFile4(str(source),'r',None,0);doc=model(res[0] if isinstance(res,tuple) else res);s.ActivateDoc3(doc.GetTitle(),False,0,0)
            finally:
                for k,v in oldi.items():s.SetUserPreferenceIntegerValue(k,v)
                s.SetUserPreferenceToggle(CONST.swVrmlStlImportAsPSMesh,oldb)
            p=typed(doc,'IPartDoc');bs=p.GetBodies2(0,False) or []
            if not bs or any(typed(b,'IBody2').Check2() for b in bs):p.ImportDiagnosis(True,False,True,0)
        else:
            doc=model(s.NewDocument(s.GetUserPreferenceStringValue(CONST.swDefaultTemplatePart),0,0,0))
            if name.startswith('Bearing_cap_'):
                rear='rear' in name;z=-12.4 if rear else 7.2
                boss(doc,'Cap_plate_26x20x2',z,z+2,rect=(-.5,-10,25.5,10),circles=[(12.5,0,6.6),(1.8,0,1.1),(23.2,0,1.1)])
                if rear:boss(doc,'Bearing_retention_lip',-10.41,-8.2,circles=[(12.5,0,8),(12.5,0,6.6)])
            elif name=='AS5600_PCB_L1':boss(doc,'PCB_25p4x17p78x1p6_M2p5',-24.15,-22.55,rect=(-.2,-8.89,25.2,8.89),circles=[(x,y,1.25) for x,y in holes])
            elif name=='AS5600_chip_L1':boss(doc,'Sensor_envelope_5x4x1p75',-22.55,-20.8,rect=(10,-2,15,2))
            elif name=='AS5600_connectors_L1':
                for k,dx in enumerate([-9.652,9.652]):boss(doc,'QT_connector_'+str(k+1),-22.55,-19.55,rect=(12.5+dx-2.1,-2.5,12.5+dx+2.1,2.5))
            elif name.startswith('688_bearing_'):
                z=-8.1 if 'rear' in name else 2.1;boss(doc,'688_envelope_D16_D8_L5',z,z+5,circles=[(12.5,0,8),(12.5,0,4)])
            elif name=='Diametric_magnet_L1':boss(doc,'Diametric_magnet_D6_L2',-18.8,-16.8,circles=[(12.5,0,3)])
            else:raise ValueError(name)
        color=[.12,.40,.55] if part['kind']=='print' else [.12,.48,.16] if 'PCB' in name else [.25,.28,.32] if 'chip' in name or 'connectors' in name else [.65,.68,.70]
        doc.MaterialPropertyValues=com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_R8,color+[1,.5,.25,.1,0,0]);doc.ForceRebuild3(False);doc.ShowNamedView2('*Isometric',7);doc.ViewZoomtofit2();assert doc.SaveAs3(str(path),0,1)==0
        p=typed(doc,'IPartDoc');row={'part':name,'path':str(path),'source':'build_encoder_leader.py cartridge_parts() and encoder-build.json','native_features':name not in imported,'solids':[{'kernel_faults':typed(b,'IBody2').Check2(),'box_m':list(typed(b,'IBody2').GetBodyBox()),'volume_m3':typed(b,'IBody2').GetMassProperties(1)[3]} for b in p.GetBodies2(0,False) or []],'surface_bodies':len(p.GetBodies2(1,False) or [])}
        ev.write_text(json.dumps(row,indent=2));print(name,'solid faults',[b['kernel_faults'] for b in row['solids']],flush=True);s.CloseDoc(doc.GetTitle())
if __name__=='__main__':main()
