"""Close only saved generated CAD documents, preserving unrelated user documents."""
from native_hardware import *
s=attach();prefix=str((ROOT/'solidworks').resolve()).lower()+'\\';closed=[];kept=[]
for raw in s.GetDocuments() or []:
    d=model(raw);path=d.GetPathName()
    if path and str(Path(path).resolve()).lower().startswith(prefix):
        if d.GetSaveFlag():kept.append({'title':d.GetTitle(),'reason':'unsaved generated document; not discarded'})
        else:title=d.GetTitle();s.CloseDoc(title);closed.append(title)
    else:kept.append({'title':d.GetTitle(),'reason':'unrelated or unnamed document'})
print(json.dumps({'closed_saved_task_documents':closed,'preserved':kept},indent=2))
