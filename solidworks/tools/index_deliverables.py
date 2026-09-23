"""List accepted deliverable files, keeping checkpoints out of the delivery index."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
paths=[]
for area in ['solidworks/parts','solidworks/hardware','ros2_ws/src/so101_description','simulation']:
 paths.extend(p for p in (ROOT/area).rglob('*') if p.is_file() and not p.name.startswith('~$') and p.suffix.lower() not in ['.pyc','.bmp'] and '__pycache__' not in p.parts)
paths.extend((ROOT/'solidworks/assemblies').glob('*_Master.SLDASM'))
paths.extend(ROOT/p for p in ['docs/source_audit.md','docs/final_report.md','docs/decision_log.md','docs/open_issues.md','solidworks/README.md','so101-mg996r/firmware/joint_mapping.md'])
paths.append(ROOT/'verification/visual_pose_comparison.md')
paths.extend((ROOT/'verification/pose_images').glob('*.png'))
rows=[]
for p in sorted(set(paths)):
 assert p.is_file(),p
 rows.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(ROOT/'verification/deliverable_files.json').write_text(json.dumps({'note':'Accepted deliverables and simulation handoffs. Checkpoints, failed trials and raw intermediate meshes are deliberately excluded. Physical and runtime limitations are in docs/final_report.md.','files':rows},indent=2));print('Indexed',len(rows),'delivered files.')
