"""Slice only the bench prototype/measurement gauges, never the unfinished arm."""
from pathlib import Path
import json,subprocess,zipfile,re,shutil,hashlib
from build_fit_test import DEST,WEB

RES=Path('/Applications/BambuStudio.app/Contents/Resources/profiles/BBL')
BIN='/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'

def resolve(path):
    data=json.loads(path.read_text());out={}
    if data.get('inherits'):
        parent=list(RES.rglob(data['inherits']+'.json'));assert len(parent)==1,parent
        out.update(resolve(parent[0]))
    for inc in data.get('include',[]):
        parent=list(RES.rglob(inc+'.json'));assert len(parent)==1,parent
        out.update(resolve(parent[0]))
    out.update(data);out.pop('inherits',None);out.pop('include',None)
    return out

def main():
    target=DEST/'slicing';target.mkdir(exist_ok=True)
    machine=resolve(RES/'machine/Bambu Lab P1S 0.4 nozzle.json')
    process=resolve(RES/'process/0.20mm Standard @BBL X1C.json')
    filament=resolve(RES/'filament/Generic PETG.json')
    machine['curr_bed_type']='Textured PEI Plate';process['curr_bed_type']='Textured PEI Plate'
    process.update({'name':'SO101 unpowered bench fit PETG 0.20',
        'wall_loops':'4','sparse_infill_density':'25%','sparse_infill_pattern':'gyroid',
        'enable_support':'1','support_type':'normal(auto)','support_on_build_plate_only':'0',
        'support_threshold_angle':'30','brim_type':'outer_only','brim_width':'5',
        'print_sequence':'by layer','enable_prime_tower':'0'})
    for name,data in [('machine',machine),('process',process),('filament',filament)]:
        (target/(name+'.json')).write_text(json.dumps(data,indent=2))
    results=[]
    for name in ['P1S_QUICK_GAUGES_ONLY','P1S_FIT_TEST_ONLY']:
        folder=target/name;folder.mkdir(exist_ok=True)
        args=[BIN,'--load-settings',str(target/'machine.json')+';'+str(target/'process.json'),
              '--load-filaments',str(target/'filament.json'),'--arrange','0','--orient','0',
              '--slice','0','--outputdir',str(folder),'--export-3mf',name+'_sliced.3mf',str(DEST/(name+'.3mf'))]
        run=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=600)
        (folder/'slicer.log').write_text(run.stdout)
        row={'plate':name,'exit_code':run.returncode,'input_sha256':hashlib.sha256((DEST/(name+'.3mf')).read_bytes()).hexdigest()}
        output=folder/(name+'_sliced.3mf')
        if run.returncode==0 and output.exists():
            with zipfile.ZipFile(output) as z:
                for file in z.namelist():
                    if file.endswith('.gcode'):
                        code=z.read(file).decode()
                        row['gcode_summary']=[l for l in code.splitlines() if re.search(r'(total estimated time|model printing time|total filament|filament used)',l,re.I)][:16]
                        row['gcode_present']=True
            shutil.copy2(output,WEB/'fit-test'/output.name)
            row['sliced_file']=output.name
        else:row['error_tail']=run.stdout[-3000:]
        results.append(row);print(json.dumps(row,indent=2),flush=True)
    (target/'results.json').write_text(json.dumps(results,indent=2))
    report=json.loads((DEST/'verification.json').read_text());report['slicer_status']='passed' if all(r.get('gcode_present') for r in results) else 'failed'
    report['slicer']={'printer':'Bambu Lab P1S','nozzle_mm':.4,'material':'Generic PETG','layer_height_mm':.2,'walls':4,'infill':'25% gyroid','support':'auto normal','brim_mm':5,'plates':results,'physical_print_verified':False}
    (DEST/'verification.json').write_text(json.dumps(report,indent=2));shutil.copy2(DEST/'verification.json',WEB/'fit-test/verification.json')

if __name__=='__main__':main()
