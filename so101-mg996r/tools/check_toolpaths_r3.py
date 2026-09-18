"""Screen sliced G-code for entirely missing mesh cross-section components.

This is a coarse extrusion-presence check, NOT a toolpath/strength certificate.
In particular it does not verify infill density or every perimeter segment.
"""
import json,re,zipfile,math,hashlib
import numpy as np
import shapely
from shapely.geometry import Polygon
from build_follower_r3 import DEST,load,transform

def paths(text):
    xy=np.zeros(2);height=None;feature='Custom';relative_e=True;e_prev=0;groups={}
    for line in text.splitlines():
        if line.startswith('; Z_HEIGHT:'):height=float(line.split(':')[1])
        elif line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
        elif line.startswith('M83'):relative_e=True
        elif line.startswith('M82'):relative_e=False
        elif line.startswith(('G0 ','G1 ','G2 ','G3 ')):
            d={k:float(v) for k,v in re.findall(r'([XYEIJ])(-?\d*\.?\d+)',line.split(';')[0])}
            end=np.array([d.get('X',xy[0]),d.get('Y',xy[1])])
            amount=d.get('E',0) if relative_e else d.get('E',e_prev)-e_prev
            if 'E' in d:e_prev=d['E']
            arc=line.startswith(('G2 ','G3 ')) and ('I' in d or 'J' in d)
            if height is not None and amount>0 and (np.linalg.norm(end-xy)>1e-6 or arc) and feature not in ['Custom','Brim'] and not feature.startswith('Support'):
                points=np.array([xy,end])
                if arc:
                    center=xy+np.array([d.get('I',0),d.get('J',0)])
                    start=math.atan2(*(xy-center)[::-1]);stop=math.atan2(*(end-center)[::-1])
                    delta=(stop-start)%(2*math.pi)
                    if line.startswith('G2 '):delta=delta-2*math.pi
                    if abs(delta)<1e-8:delta=2*math.pi
                    angles=np.linspace(start,start+delta,max(2,int(math.ceil(abs(delta)/math.radians(3)))+1))
                    radius=np.linalg.norm(xy-center);points=center+radius*np.column_stack([np.cos(angles),np.sin(angles)])
                groups.setdefault(round(height,5),[]).extend(np.stack([points[:-1],points[1:]],axis=1).tolist())
            xy=end
    return {h:shapely.STRtree(shapely.linestrings(np.asarray(p))) for h,p in groups.items()}

def main():
    layout=json.loads((DEST/'plate-report.json').read_text());rows=[];files={}
    for plate in layout['plates']:
        p=DEST/plate['slicer']['sliced_file']
        files[str(p.relative_to(DEST))]=hashlib.sha256(p.read_bytes()).hexdigest()
        with zipfile.ZipFile(p) as z:code=z.read(next(n for n in z.namelist() if n.endswith('.gcode'))).decode()
        samples=paths(code);missing=[];checked=0
        for entry in plate['entries']:
            s=transform(load(DEST/'print-parts'/(entry['part']+'.stl')),np.asarray(entry['matrix']).reshape(4,4).T)
            max_height=entry['bounds_mm'][1][2]
            for k in range(1,int(math.ceil(max_height/.2))+1):
                h=round(k*.2,5);z=h-.1
                contours=s.slice(z).to_polygons()
                path_index=samples.get(h)
                for c in contours:
                    if len(c)<3:continue
                    area=.5*np.sum(c[:,0]*np.roll(c[:,1],-1)-c[:,1]*np.roll(c[:,0],-1))
                    if area<2:continue # hole contours / sub-2 mm² features not certified
                    polygon=Polygon(c)
                    if not polygon.is_valid:polygon=polygon.buffer(0)
                    checked+=1
                    # A 0.3 mm buffer includes extrusion centrelines at a thin
                    # boundary and small mesh/slicer numerical differences.
                    covered=path_index is not None and len(path_index.query(polygon.buffer(.3),predicate='intersects'))>0
                    if not covered:missing.append({'part':entry['part'],'print_z_mm':h,'slice_z_mm':z,'outer_area_mm2':float(area),'bounds':list(polygon.bounds)})
        diagnostics=[l for l in (p.parent/'slicer.log').read_text().splitlines() if '[error]' in l or '[warning]' in l]
        row={'plate':plate['id'],'cross_section_components_screened':checked,'missing_component_candidates':missing,
             'slicer_diagnostics':diagnostics,'coarse_screen_passed':not missing}
        rows.append(row);print(plate['id'],checked,'components;',len(missing),'missing candidates;',len(diagnostics),'diagnostics',flush=True)
    report={'method':'At each nominal 0.20 mm model layer, test whether each positive-winding mesh cross-section contour >2 mm² intersects a non-support extrusion segment (0.3 mm tolerance; arcs approximated in 3-degree segments). Holes, fine features, exact bead widths, complete perimeter coverage and load strength are not certified.',
            'files':files,'plates':rows,'all_coarse_screens_passed':all(r['coarse_screen_passed'] for r in rows)}
    (DEST/'toolpath-screen.json').write_text(json.dumps(report,indent=2))

if __name__=='__main__':main()
