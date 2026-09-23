"""Summarize completed evidence without promoting unknown properties to facts."""
from pathlib import Path
import json,yaml,csv
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text())
f=read('solidworks/evidence/joint_motion_measurements.json');l=read('solidworks/evidence/leader_joint_motion_measurements.json');lg=read('verification/leader_geometry_comparison.json')
fm=read('verification/follower_master_reopen.json');lm=read('verification/leader_master_reopen.json')
fc=read('verification/cad_mesh_motion_interference.json');lc=read('verification/leader_cad_mesh_motion_interference.json')
urdf=read('verification/urdf_validation.json');mj=read('verification/mujoco_urdf_import.json');integrity=read('verification/original_file_integrity.json')
assert len(f)==len(l)==28 and all(x['kinematic_pass'] for x in f+l)
assert all(len(p.get('native_limits',[]))==6 and all(x['pass'] and x.get('active') for x in p['native_limits']) for p in f+l)
assert len(lg)==18 and all(x['pass'] for x in lg)
assert all(r['pass'] for m in [fm,lm] for r in m['configurations'])
assert all(read(f'verification/{name}_constraint_mobility.json')['pass'] for name in ['follower','leader'])
assert all(r['pass'] for r in urdf['pose_regressions']) and all(r['pass'] for r in mj['kinematic_regression'])
for name in ['follower','leader']:
    assert not read(f'solidworks/evidence/{name}_mcp_pose_handoff.json').get('isError',False)
    assert read(f'solidworks/evidence/{name}_final_controller_positions.json')['pass']
joints=yaml.safe_load((ROOT/'simulation/joint_map.yaml').read_text())['joints']
table=['| Joint | Parent → child | Axis / positive sign | Zero; min…max (deg) | Servo channel / sensor mux | Motion |','|---|---|---|---|---|---|']
for j in joints:table.append(f"| {j['joint_name']} | {j['parent_link']} → {j['child_link']} | local +Z / right-hand; default +1 | 0; {j['minimum_degrees']}…{j['maximum_degrees']} | {j['servo_channel']} / {j['servo_channel']} | Both CAD assemblies PASS |")
collisionlines=[]
for robot,c in [('Follower',fc),('Leader',lc)]:
    for p in c['tested_poses']:
        large=[h for h in p['intersections'] if h['above_source_report_threshold']]
        if p['table_penetrations']:
            collisionlines.append(f"- {robot} `{p['pose']}`: {len(p['table_penetrations'])} components below table Z=0; lowest {min(x['lowest_vertex_z_mm'] for x in p['table_penetrations']):.3f} mm.")
        if robot=='Leader' and large:
            collisionlines.append(f"- Leader `{p['pose']}`: {len(large)} reported overlaps above 0.5 mm³; largest {max(h['volume_mm3'] for h in large):.6f} mm³. Inspect pair details in `verification/leader_cad_mesh_motion_interference.json`.")
leadermax=max(max(x['bidirectional_surface_error_mm']) for x in lg)
text=f'''# SO-101 SolidWorks reconstruction report

Engineering prototypes: **not physically tested or payload rated**. The current R3 six-MG996R follower and L1 passive six-AS5600 leader were reconstructed in SolidWorks 2026 SP4.1 through a task-local MCP bridge and the installed COM API. Original geometry, browser viewer, P1S layouts and firmware were preserved. All 330 original files match their saved hashes; see `verification/original_file_integrity.json`.

## Reconstruction

| Deliverable | Location | Instances / unique parts | Moving joints | Native mates / fixed components |
|---|---|---|---|---|
| Follower | `solidworks/assemblies/SO101_Follower_Master.SLDASM` | 19 / 9 | 5 arm + 1 jaw | 36 total; 30 active in FREE_MOTION / base only |
| Passive leader | `solidworks/assemblies/SO101_Leader_Master.SLDASM` | 73 / 18 | 5 arm + 1 trigger | 90 total; 84 active in FREE_MOTION / base only |

The leader comprises 37 printed instances and 36 hardware-envelope instances. Native feature hardware includes the MG996R envelope, metal horn, two bearing caps, PCB/chip/connectors, bearings and magnet. Custom printed geometry is mostly source-preserving imported solid base features with native datum sketches/axes/planes. This is **not** a recovered, fully parametric manufacturing feature history.

Final loaded references contain {fm['solid_body_count_unique_parts']} follower solid bodies and {lm['solid_body_count_unique_parts']} leader solid bodies across their unique parts. All return zero kernel faults. The leader additionally contains {lm['surface_body_count_unique_parts']} healthy zero-thickness surface bodies preserving source artifacts. Native saved configuration checks pass with no reported mate errors. Only one root is grounded in each assembly.

Open one master at a time on a memory-limited workstation. Keep `solidworks/parts/` and `solidworks/hardware/` beside the assemblies. `solidworks/README.md` explains the controls and reference paths. Checkpoints and rejected trials are retained separately.

## Joint table

{chr(10).join(table)}

Axes above are **local joint-frame +Z**, not all global vertical. Full measured origin XYZ/RPY and component mappings are in `simulation/joint_map.yaml` and `simulation/leader_joint_map.yaml`. Source frame: +X forward at HOME, +Y left, +Z up. Source viewer X separation is removed; CAD retains +2.4 mm tabletop placement. URDF base coordinates omit that scene placement; the explicit relation is in `simulation/cad_rig.json`.

ZERO = [0,0,0,0,0,0], HOME = [0,-25,35,0,0,20], MID_RANGE = [0,0,0,0,0,35] degrees. These are saved configurations. Native Mate Controllers also store 12 individual limit poses. Native mate angle = 90° + logical angle. The limits are **SOURCE VERIFIED software/preview bounds**, not measured safe mechanical stops. Do not command a physical robot merely because a pose is within these bounds.

The jaw and trigger are direct revolute DOFs; no additional coupled linkage was invented. Leader trigger mesh mounting index +15° is retained in its instance transform. Firmware leader ZERO capture is performed at HOME: q = home + sign × signed_wrap_12bit(raw − zero_counts) × 360/4096. Actual signs/count offsets and servo horn indexing remain UNVERIFIED.

## Accuracy

- **SOURCE VERIFIED:** source register and conflict decisions in `docs/source_audit.md`; modified R3/L1 geometry takes precedence over stock STEP files from a different revision. Detailed source dimensions, generator constants and original transforms were retained rather than averaged.
- **CAD MEASURED / CALCULATED:** follower printed surfaces compared using all vertices plus 30,000 samples per direction (50,000 for the partitioned forearm). Largest observed error: 0.001958407 mm. Base and wrist miss the stricter 0.001 mm trial, but all seven pass the source generator's 0.005 mm tolerance. This is sampled agreement, not mathematical identity.
- **CAD MEASURED / CALCULATED:** all 18 adopted leader part exports pass the recorded 0.005 mm surface, 0.001 mm bounds and per-type volume gates. Largest observed bidirectional surface discrepancy: {leadermax:.9f} mm. Full values, stricter 1 µm outcomes and native-circle tessellation differences are in `verification/leader_geometry_comparison.json`.
- Follower forearm uses three valid solids in one rigid part. Leader base and forearm use four each. The leader forearm includes a disclosed 0.00001 mm internal numerical gap, approximately 0.0238 mm³ removed, to resolve coincident source facets rejected by the CAD kernel. Its zero-thickness source patch is preserved as eight surface facets; three trigger patches are likewise retained. No physical thickness was fabricated.
- Across 28 actual mate-solved poses, maximum follower component position/orientation difference is {max(p['max_position_error_mm'] for p in f):.9g} mm / {max(p['max_angle_error_deg'] for p in f):.9g}°. Leader maximum is {max(p['max_position_error_mm'] for p in l):.9g} mm / {max(p['max_angle_error_deg'] for p in l):.9g}°. Every component, including hardware, was compared to source forward kinematics.
- Hole/interface exteriors are included in the surface comparisons. Not every hole was reconstructed as an editable dimension. Unrepresented screws, cables and internal commercial-component details were not inferred into CAD.

## Motion validation

Every joint was exercised independently at minimum, zero, maximum and return; HOME and a combined pose were tested. Both assemblies pass all 28 recorded pose comparisons and the three saved-configuration reopen checks. Evidence is under `solidworks/evidence/`, plus `verification/follower_master_reopen.json`, `leader_master_reopen.json`, `joint_verification.csv` and `leader_joint_verification.csv`.

The final regression reads back all six genuine native Limit Angle feature types and their lower/upper bounds at every pose. Earlier fixed-angle and converted-mate trials are retained as superseded checkpoint evidence. The final limits were created with CreateMateData/CreateMate and explicit plane entities. Their current dimensions retain the default native driving state; making these dimensions driven caused the rejected bounds drift. Explicit joint-axis references prevent alternate angle solutions when configurations change. All six pose values are written explicitly per configuration, including unchanged values, to avoid stale inherited dimension state. Six separate optional angle holders make ZERO/HOME/MID_RANGE repeatable; these snapshots suppress the redundant range mates. FREE_MOTION suppresses the holders and activates all six limits. This avoids native redundant-mate warnings in the fixed snapshots. Only the base is fixed. Native component status with active limit mates is recorded separately and is not used as a numerical DOF count; suppression of a limit changes that diagnostic. The hinge graph and measured joint movement establish the reported articulation scope. Every native mate's actual component entities are audited against the source adjacency/rigid groups.

Constraint-matrix analysis gives six independent rotational freedoms and no additional infinitesimal freedoms at HOME for each native mate graph. This is **CALCULATED**, not a SolidWorks kernel DOF diagnostic or a mouse-drag test. Native mate-driven movement is separately CAD MEASURED.

Follower API drag probes and a leader direct-dimension solver-branch trial failed and were rejected. Saved masters were recovered/retested. Use named configurations and native mate controls; free mouse dragging remains UNVERIFIED. No accepted pose is produced by assigning arbitrary component transforms.

Discrete volumetric collision checks cover 15 named measured poses for each assembly (14 distinct joint vectors because J6_MIN equals ZERO), all component pairs, with no pair exclusion. Source zero-thickness leader sheets are retained in visual geometry but have no solid volume to intersect. Raw overlaps down to 0.00001 mm³ are recorded; 0.5 mm³ is the inherited source report threshold, not a physical clearance allowance. Follower native SolidWorks HOME interference independently confirms six intended servo shaft/horn engagements of about 9.032 mm³. No other follower sampled internal overlap exceeds 0.5 mm³; smaller fixed overlaps remain recorded.

{chr(10).join(collisionlines) if collisionlines else 'No table penetration or leader overlap above the source threshold occurred in these specific samples.'}

The inherited L1 source report separately checks 72 poses, with two folded combined collision failures and 11 table-collision poses. Its cartridge checks cover 72 rotor samples, six interfaces and a source magnet-to-chip gap of 2 mm. Those are labelled source results; they are not substituted for current CAD measurements. Neither discrete set certifies swept motion, cables, physical fit or safe payload operation. Existing geometry was not redesigned to remove these limitations.

## Simulation and firmware

| Output | Status |
|---|---|
| `ros2_ws/src/so101_description/` | Xacro/XML, parser, connected tree (8 links/7 joints/6 moving), mesh paths/units and 28 pose regressions PASS. ROS 2 build/RViz not run; tooling was not found in the accessible environment. |
| `simulation/mujoco/so101_import_test.urdf` | MuJoCo 3.14.0 imports 6 joints; all 28 FK regressions PASS. Automatically inferred masses are explicitly rejected. No physical-dynamics stepping accepted. |
| `simulation/mujoco/so101.xml` | Structural MJCF template with inferred inertia disabled. Expected load rejection was tested. Requires real inertias and accepted contact geometry before dynamics. |
| `simulation/isaac/` | Self-contained validated URDF, meshes, importer requirements and pose references prepared. Isaac import/articulation/USD not tested; no USD fabricated. |
| `simulation/inertial_properties.yaml` | CAD unit-density geometric integrals and per-rigid-link contributions provided; physical mass, COM and inertia remain null/UNVERIFIED. |
| `so101-mg996r/firmware/joint_mapping.md` | Six PCA9685 channels 0–5 mapped to logical joints; ESP32 and leader AS5600/TCA9548A addresses, signs, HOME/zero and calibration relationships documented. Original firmware unchanged. |

Follower collision geometry uses source-envelope servo box/cylinder unions and exact CAD print/horn tessellation. Servo primitive union comparison passed (maximum sampled deviation 0.000324 mm). A fine convex print decomposition was rejected as impractically fragmented. Concave print meshes are retained for geometric inspection; validated convex dynamic-contact proxies are still outstanding. Simulators must not silently replace each concave print with one convex hull.

Firmware defaults are 1500 µs neutral, +1 sign, 5.555556 µs/degree, direct ratio 1:1. The 0.2° per 20 ms update ceiling is a 10°/s commanded slew, not a measured servo capability. No supported effort/payload rating is assigned.

## Unverified properties and next physical validation

1. Measure printed link/hardware masses, centers of mass and inertia or validate a defensible infill-aware model. Generic PETG, four walls and 25% gyroid do not justify uniform-solid mass. The plate filament total includes support/brim. Genuine TowerPro's 55 g reference is not confirmed for the user's generic units.
2. Check actual servo shaft/horn fit, bearing seats, fastener stack-ups, screw locations/retention and mounting tolerances. Some fasteners are listed in the source BOM but not spatially represented in the published assembly. Source zero-thickness patches and multipart seams need manufacturing review.
3. Measure mechanical stops and table/self-clearance over continuous motion, including cable routing and pinch regions. Software bounds are not verified physical limits.
4. Calibrate each servo neutral, sign, horn index, endpoint and backlash; each AS5600 zero count, direction, magnet alignment and usable sensing gap. Check the leader-to-follower mapping on a supported, power-limited prototype.
5. Measure torque/speed, friction, damping, compliance, contact behavior, power/current limits, thermal behavior and payload capacity. No values were invented to make a simulator run.
6. Validate free mouse dragging if desired. Named configurations and mate-definition controls are the tested CAD movement path.
7. Complete accepted convex contact proxies and run ROS 2 visualization, MuJoCo physical dynamics and Isaac articulation/USD validation when the required measured data/tooling are available.

## Evidence and reproducibility

The final task-local MCP command successfully set and saved HOME in both masters with all six native limits active and no mate errors. All 15 saved Mate Controller positions were then read back; see `solidworks/evidence/follower_mcp_pose_handoff.json`, `solidworks/evidence/leader_mcp_pose_handoff.json` and the two `*_final_controller_positions.json` files in that evidence directory. The follower is left open in its saved HOME configuration for handoff.

Five paired native SolidWorks and MuJoCo visual views (ZERO, J1_MAX, J2_MIN, MULTI and HOME) are in [the visual pose comparison](../verification/visual_pose_comparison.md). Their complete silhouettes and joint orientations were inspected after fitting each camera to its pose. Numerical component-transform regressions accompany the images; camera/shading differences are not treated as geometric errors.

`docs/source_audit.md`, `docs/decision_log.md`, `docs/open_issues.md`, `verification/original_vs_solidworks.md`, the two joint maps, raw pose/part evidence, and source hash manifest identify what is SOURCE VERIFIED, CAD MEASURED, CALCULATED or UNVERIFIED. The delivered-file index is `verification/deliverable_files.json`. Scripts are in `solidworks/tools/`; failed/rejected trials are explicitly separate from delivered masters. Do not rerun raw reconstruction scripts over accepted parts without first reading their checkpoint/adoption assumptions.
'''
(ROOT/'docs/final_report.md').write_text(text,encoding='utf-8')
(ROOT/'docs/progress.md').write_text('''# Reconstruction status

The delivered SolidWorks masters, geometry comparisons, native mate-driven motion, saved configurations, firmware mappings and available kinematic simulation checks are complete. Quantitative results and limitations are in `final_report.md`.

- Source audit: 330 original files inspected and hash-preserved; R3 follower and L1 leader revisions retained.
- Follower: 19 instances, nine unique parts, one fixed base, 36 total mates (30 active in FREE_MOTION) and six revolute DOFs.
- Leader: 73 instances, 18 unique parts, one fixed base, 90 total mates (84 active in FREE_MOTION) and six passive revolute DOFs.
- Both assemblies: 28 native mate-driven pose checks, three stored-configuration reopen checks, six-DOF constraint-rank calculation and 15 discrete all-pair collision checks completed. Existing table/collision limitations remain documented.
- Geometry: native hardware features where practical; imported solid base geometry with native joint datums for complex prints. Source seams and zero-thickness artifacts are disclosed. No recovered full parametric print history is claimed.
- ROS description: Xacro/parser/tree/units/paths and 28-pose regressions pass. MuJoCo URDF-import kinematics pass the same poses. Visual comparisons are recorded separately.
- Physical mass, COM, inertia, actuator/contact properties, calibration, payload and continuous clearances remain UNVERIFIED. Concave prints still need accepted dynamic contact proxies. The MJCF structural template intentionally does not run physical dynamics without real inertias.
- ROS 2/RViz and Isaac import/USD were not run in this environment. Their assets and requirements are prepared; no successful runtime claim is made.
- Free mouse dragging is unverified. Native mate controls and named configurations are the tested movement path.

Engineering prototypes: not physically tested or payload rated. See `open_issues.md` for the outstanding physical/tooling requirements.
''',encoding='utf-8')
comparison=ROOT/'verification/original_vs_solidworks.md'
prior=comparison.read_text().split('## Leader L1 adopted geometry')[0].rstrip()
comparison.write_text(prior+f'''

## Leader L1 adopted geometry

All 18 adopted native-file exports pass their recorded comparison gates. Largest sampled bidirectional source/CAD discrepancy is {leadermax:.9f} mm; individual bounds, volumes and stricter 1 µm checks are in `leader_geometry_comparison.json`. There are {lm['solid_body_count_unique_parts']} healthy solid bodies across the unique components and {lm['surface_body_count_unique_parts']} healthy source-artifact surface bodies. Base/forearm solid partitions and the 0.00001 mm forearm internal separation are disclosed numerical preservation measures.

The separate leader master contains 73 instances, one fixed base and 90 total native mates (84 active in FREE_MOTION). All 28 measured poses pass, maximum component position difference {max(p['max_position_error_mm'] for p in l):.9g} mm and orientation difference {max(p['max_angle_error_deg'] for p in l):.9g} degrees. All three stored configurations pass final readback. The same six logical joints map through six AS5600 channels to the follower, with the source 14 mm wrist extension and +15 degree trigger mesh index retained.

Current leader volumetric collision checks use actual individually exported CAD solid bodies at 15 measured poses. Their pairwise results and table penetrations are in `leader_cad_mesh_motion_interference.json`; source zero-thickness surfaces are excluded only from solid-volume intersections. The inherited source 72-pose report remains separate. These are discrete checks, not collision-free swept-motion certification.

Both assembly constraint graphs calculate six independent rotations at HOME, with no additional infinitesimal freedom. This is a mathematical topology check, not freehand-drag verification. Failed drag/direct-dimension trials are rejected evidence. See `../docs/final_report.md` for the complete acceptance scope.
''',encoding='utf-8')
print('Wrote evidence-gated final report.')
