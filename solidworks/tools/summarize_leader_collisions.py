from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[2]
data=json.loads((ROOT/'verification/leader_cad_mesh_motion_interference.json').read_text());byname={p['pose']:p for p in data['tested_poses']}
p=ROOT/'verification/leader_joint_verification.csv'
with p.open(newline='') as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
for j,row in enumerate(rows):
    notes=[]
    for suffix in ['MIN','MAX']:
        pose=byname[f'J{j+1}_{suffix}'];large=[h for h in pose['intersections'] if h['above_source_report_threshold']];notes.append(f"{suffix}: {len(large)} overlaps >0.5mm3, {len(pose['table_penetrations'])} table penetrations")
    row['Collision result']='; '.join(notes)+'; discrete checks only; raw smaller overlaps retained'
    row['Evidence']+='; verification/leader_cad_mesh_motion_interference.json'
with p.open('w',newline='') as f:writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
print('Updated six leader joint collision rows.')
