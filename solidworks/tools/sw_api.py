"""Attach to the user's running SolidWorks; never starts a replacement session."""
from pathlib import Path
import pythoncom
import win32com.client as com
from win32com.client import gencache

API = Path(r'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS')
def library(name):
    a=pythoncom.LoadTypeLib(str(API/(name+'.tlb'))).GetLibAttr()
    return gencache.EnsureModule(a[0],a[1],a[3],a[4])
SW=library('sldworks')
CONST=library('swconst').constants
def attach():
    return SW.ISldWorks(com.GetActiveObject('SldWorks.Application')._oleobj_)
def model(obj):
    return SW.IModelDoc2(obj._oleobj_)
if __name__=='__main__':
    s=attach(); d=model(s.ActiveDoc)
    print({'revision':s.RevisionNumber(),'active':d.GetTitle(),'path':d.GetPathName(),'generated_api':SW.__file__})
