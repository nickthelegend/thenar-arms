from check_assembly_pose import *
s,doc,asm,cs=connect()
poses={'ZERO':[0]*6,'HOME':[0,-25,35,0,0,20],'MID_RANGE':[0,0,0,0,0,35],'Default':[0]*6}
for name,q in poses.items():
    for j,angle in enumerate(q):
        f=mate_features(doc)[f'J{j+1}_Source_preview_limits']
        dim=typed(typed(f.GetFirstDisplayDimension(),'IDisplayDimension').GetDimension2(0),'IDimension')
        status=dim.SetSystemValue3(math.radians(90+angle),CONST.swSetValue_InSpecificConfigurations,com.VARIANT(pythoncom.VT_ARRAY|pythoncom.VT_BSTR,[name]))
        assert status==0,(name,j,status)
    print('Stored configuration angles',name,q,flush=True)
doc.ForceRebuild3(False);assert doc.SaveAs3(doc.GetPathName(),0,1)==0
