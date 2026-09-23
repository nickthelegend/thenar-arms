"""Export active CAD geometry in its original part frame for independent comparison."""
from sw_api import *
from native_hardware import typed
import sys,json
ROOT=Path(__file__).resolve().parents[2]
def main(source,dest):
    s=attach();d,e,w=s.OpenDoc6(str(source),1,1,'',0,0);assert d is not None,(e,w)
    doc=model(d);s.ActivateDoc3(doc.GetTitle(),False,0,0)
    ints={CONST.swSTLQuality:CONST.swSTLQuality_Custom,CONST.swExportStlUnits:CONST.swMM}
    toggles={CONST.swSTLBinaryFormat:True,CONST.swSTLDontTranslateToPositive:True,CONST.swSTLShowInfoOnSave:False,CONST.swSTLPreview:False}
    doubles={CONST.swSTLDeviation:1e-6,CONST.swSTLAngleTolerance:.02}
    oldi={k:s.GetUserPreferenceIntegerValue(k) for k in ints};oldt={k:s.GetUserPreferenceToggle(k) for k in toggles};oldd={k:s.GetUserPreferenceDoubleValue(k) for k in doubles}
    try:
        for k,v in ints.items():s.SetUserPreferenceIntegerValue(k,v)
        for k,v in toggles.items():s.SetUserPreferenceToggle(k,v)
        for k,v in doubles.items():s.SetUserPreferenceDoubleValue(k,v)
        error=doc.SaveAs3(str(dest),0,1);assert error==0,error
        print(json.dumps({'source':str(source),'export':str(dest),'save_error':error}),flush=True)
    finally:
        for k,v in oldi.items():s.SetUserPreferenceIntegerValue(k,v)
        for k,v in oldt.items():s.SetUserPreferenceToggle(k,v)
        for k,v in oldd.items():s.SetUserPreferenceDoubleValue(k,v)
if __name__=='__main__':main(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
