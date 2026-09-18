"""P1S PETG slicing of the actual R3 printing units, not the stock plates."""
import json,subprocess,zipfile,re,hashlib,tempfile,os
from build_follower_r3 import DEST
from slice_fit_test import resolve,RES,BIN

def main():
    target=DEST/'slicing';target.mkdir(exist_ok=True)
    machine=resolve(RES/'machine/Bambu Lab P1S 0.4 nozzle.json')
    process=resolve(RES/'process/0.20mm Standard @BBL X1C.json')
    filament=resolve(RES/'filament/Generic PETG.json')
    machine['curr_bed_type']='Textured PEI Plate';process['curr_bed_type']='Textured PEI Plate'
    process.update({'name':'SO101 MG996R R3 PETG prototype',
        'wall_loops':'4','sparse_infill_density':'25%','sparse_infill_pattern':'gyroid',
        'wall_generator':'arachne',
        'enable_support':'1','support_type':'normal(auto)','support_on_build_plate_only':'0',
        'support_threshold_angle':'30','brim_type':'outer_only','brim_width':'5',
        'print_sequence':'by layer','enable_prime_tower':'0'})
    for name,data in [('machine',machine),('process',process),('filament',filament)]:
        (target/(name+'.json')).write_text(json.dumps(data,indent=2))
    report=json.loads((DEST/'plate-report.json').read_text());results=[]
    for plate in report['plates']:
        name=plate['id'];folder=target/name;folder.mkdir(exist_ok=True)
        source=DEST/'plates'/(name+'.3mf')
        args=[BIN,'--load-settings',str(target/'machine.json')+';'+str(target/'process.json'),
              '--load-filaments',str(target/'filament.json'),'--arrange','0','--orient','0',
              '--slice','0','--outputdir',str(folder),'--export-3mf',name+'_sliced.3mf',str(source)]
        # Keep our slicer scratch files on the workspace volume, not a full boot disk.
        scratch=tempfile.mkdtemp(prefix='slicer-',dir=target)
        run=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=600,env={**os.environ,'TMPDIR':scratch+'/'})
        (folder/'slicer.log').write_text(run.stdout)
        row={'plate':name,'exit_code':run.returncode,'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
        row['diagnostics']=[l for l in run.stdout.splitlines() if '[error]' in l or '[warning]' in l]
        out=folder/(name+'_sliced.3mf')
        if run.returncode==0 and out.exists():
            with zipfile.ZipFile(out) as z:
                gcodes=[n for n in z.namelist() if n.endswith('.gcode')]
                row['gcode_present']=bool(gcodes)
                row['gcode_summary']=[]
                for file in gcodes:
                    code=z.read(file).decode()
                    row['gcode_summary'] += [l for l in code.splitlines() if re.search(r'(total estimated time|model printing time|total filament weight)',l,re.I)]
            row['sliced_file']=str(out.relative_to(DEST))
        else:row['error_tail']=run.stdout[-4000:]
        plate['slicer']=row;results.append(row);print(json.dumps(row),flush=True)
        (target/'results.json').write_text(json.dumps(results,indent=2))
    report['sliced']=all(r.get('gcode_present') for r in results)
    report['sliced_downloads_released']=False
    report['release_note']='Geometry only: successful export is not clearance. Resolve diagnostics and inspect all sliced layers before a full print.'
    report['settings']={'printer':'Bambu Lab P1S','nozzle_mm':.4,'layer_height_mm':.2,
                        'filament':'Generic PETG','bed':'Textured PEI','walls':4,'wall_generator':'arachne','infill':'25% gyroid',
                        'support':'normal(auto), 30 degrees','brim_mm':5}
    (DEST/'plate-report.json').write_text(json.dumps(report,indent=2))

if __name__=='__main__':main()
