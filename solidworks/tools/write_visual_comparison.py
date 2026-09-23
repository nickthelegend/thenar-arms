from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'verification/pose_images'
sw=json.loads((out/'solidworks_render_scope.json').read_text());mj=json.loads((out/'mujoco_render_scope.json').read_text());rows=[]
for pose in sw['poses']:
 name=pose['pose'];assert pose['q_degrees']==mj['poses'][name];assert not pose['mate_errors'] and max(pose['max_position_error_mm'],pose['max_angle_error_deg'])<.001
 for engine in ['solidworks','mujoco']:assert (out/f'{engine}_{name}.png').is_file()
 rows.append(f"## {name}\n\nJoint degrees: {pose['q_degrees']}. Native CAD/source position discrepancy: {pose['max_position_error_mm']:.9g} mm.\n\nSolidWorks:\n\n![SolidWorks {name}]({(out/f'solidworks_{name}.png').as_posix()})\n\nMuJoCo visual geometry:\n\n![MuJoCo {name}]({(out/f'mujoco_{name}.png').as_posix()})\n")
(ROOT/'verification/visual_pose_comparison.md').write_text('''# Canonical visual pose comparison

Native SolidWorks views and MuJoCo URDF visual renders use the same five joint vectors. Camera framing, material shading and scene origins differ; these are visual orientation/silhouette checks, not a pixel-equality test. All 19 component transforms are checked numerically in each captured CAD pose; the full 28-pose URDF/MuJoCo regressions are recorded separately. MuJoCo uses forward kinematics only. Inferred physical masses are rejected and no dynamics stepping is claimed.

'''+ '\n'.join(rows));print('Wrote five paired canonical views.')
