from native_hardware import *
s=attach()
for name in ['SO101_Follower_Master.SLDASM','SO101_Leader_Master.SLDASM']:
 p=ROOT/'solidworks/assemblies'/name;raw=s.GetOpenDocumentByName(str(p))
 if raw is not None:
  d=model(raw);assert Path(d.GetPathName()).resolve()==p.resolve();s.CloseDoc(d.GetTitle());print('Closed generated master for fresh handoff check:',name,flush=True)
