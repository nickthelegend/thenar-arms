from native_hardware import *
s=attach();prefix=str((ROOT/'solidworks').resolve()).lower()+'\\'
for raw in s.GetDocuments() or []:
 d=model(raw);p=d.GetPathName()
 if p and str(Path(p).resolve()).lower().startswith(prefix) and p.lower().endswith('.sldprt'):
  if d.GetSaveFlag():assert d.SaveAs3(p,0,1)==0
  title=d.GetTitle();s.CloseDoc(title);print('Saved/closed generated part',title,flush=True)
