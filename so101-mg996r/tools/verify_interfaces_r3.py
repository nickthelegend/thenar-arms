"""Independent nominal insertion and fastener-land tests on exported R3 files."""
import json,hashlib
import numpy as np
from build_follower_r3 import DEST,OWNERS,DRIVEN,context,load,transform,cyl,servo

def main():
    m,ss,ps,sm,pm=context();rows=[]
    units=json.loads((DEST/'build-report.json').read_text())['print_units']
    by_source={source:u for u in units for source in u['source_parts']}
    for j,(owner,child) in enumerate(zip(OWNERS,DRIVEN)):
        hu,cu=by_source[owner],by_source[child]
        holder=transform(load(DEST/'print-parts'/hu['file']),np.linalg.inv(sm[j])@pm[hu['anchor_source_frame']])
        driven=transform(load(DEST/'print-parts'/cu['file']),np.linalg.inv(sm[j])@pm[cu['anchor_source_frame']])
        insertion=[]
        for dz in np.linspace(0,65,27):
            insertion.append({'lift_mm':float(dz),'intersection_mm3':max(0,(holder^servo(0,False).translate((0,0,dz))).volume())})
        lands=[]
        for x in [-22.7,26.8]:
            for y in [-5,5]:
                # Material beneath a 7 mm washer footprint, excluding the slot.
                area=(holder^cyl(3.5,-5.6,-1.8,x,y)).volume()/3.8
                passage=(holder^cyl(1.5,-10,1.5,x,y)).volume()
                lands.append({'centre_mm':[x,y],'mean_support_area_mm2':area,'M3_shank_intersection_mm3':max(0,passage)})
        horn_lands=[]
        for dx,dy in [(7,0),(-7,0),(0,7),(0,-7)]:
            x,y=12.5+dx,dy
            area=(driven^cyl(3.2,16.8,22.6,x,y)).volume()/5.8
            hole=(driven^cyl(1.5,16.8,26,x,y)).volume()
            horn_lands.append({'centre_mm':[x,y],'mean_head_support_area_mm2':area,'M3_shank_intersection_mm3':max(0,hole)})
        row={'joint':j,'holder':owner,'driven':child,'insertion':insertion,'tab_lands':lands,'horn_lands':horn_lands,
             'insertion_passed':all(r['intersection_mm3']<.5 for r in insertion),
             'four_tab_lands_present':all(r['mean_support_area_mm2']>=12 and r['M3_shank_intersection_mm3']<.05 for r in lands),
             'four_horn_lands_present':all(r['mean_head_support_area_mm2']>=12 and r['M3_shank_intersection_mm3']<.05 for r in horn_lands)}
        rows.append(row);print(j,row['insertion_passed'],row['four_tab_lands_present'],row['four_horn_lands_present'],flush=True)
    report={'revision':'R3','physical_tested':False,'joints':rows,
            'method':'Exported joined STL re-import. Hornless servo translated +Z at 27 heights; 7 mm tab-washer footprints through 4 mm ledges, and 6.4 mm horn-head footprints through 6 mm printed horn plates.',
            'scope':'Nominal fit only; no strength/load proof. Servo is inserted before the driven link is attached.',
            'all_checks_passed':all(r['insertion_passed'] and r['four_tab_lands_present'] and r['four_horn_lands_present'] for r in rows),
            'files':{str(p.relative_to(DEST)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((DEST/'print-parts').glob('*.stl'))}}
    (DEST/'interface-check.json').write_text(json.dumps(report,indent=2))

if __name__=='__main__':main()
