# SolidWorks reconstruction

Engineering prototypes: not physically tested or payload rated. The existing R3 follower and L1 leader remain the geometric references; original CAD, print layouts, browser viewer and firmware were not redesigned.

Open `assemblies/SO101_Follower_Master.SLDASM` or `assemblies/SO101_Leader_Master.SLDASM` after their verification status is recorded in `../docs/final_report.md`. Keep the `parts/` and `hardware/` directories together with the assemblies so references resolve. Checkpoints and failed trials are retained separately and are not production substitutes.

The follower has 19 instances and six revolute joints, including the direct-drive moving jaw. The passive leader has 73 instances: 37 prints and 36 hardware envelopes, with six AS5600 sensing joints. Each assembly grounds only its base. Purchased envelopes, bearing caps and the source-surface patches use native features where practical. Most custom print geometry is retained as imported solid base features with native joint sketches, axes and planes; a fully editable manufacturing feature history has not been recovered.

## Move the joints

Use the ConfigurationManager to select **ZERO**, **HOME** or **MID_RANGE** for repeatable snapshots. These activate six optional pose-holding angle mates and suppress the redundant range mates. Select **FREE_MOTION** to suppress the holders and activate the six native Limit Angle mates, giving six bounded rotational freedoms. Select HOME before FREE_MOTION when you want to start from HOME. The named Mate Controller (`Follower_Joint_Poses` / `Leader_Joint_Poses`) operates the pose holders and stores individual minimum and maximum poses as well.

For scripted movement, use `tools/set_robot_pose.py follower 0 -25 35 0 0 20` (or `leader`) with the project Python environment. Add `--save` only to persist that pose. The task-local MCP tool `set_robot_joint_pose` accepts the same six logical degree values. It uses native mate solving, preserves all range properties and checks the resulting component transforms. Direct edits through the older API trial scripts can collapse limit bounds; use the supplied range-preserving helper.

In the Mates folder, `J1_Source_preview_limits` through `J6_Source_preview_limits` define the source ranges. `J1_Pose_driver` through `J6_Pose_driver` are the optional snapshot holders. They correspond to shoulder pan, shoulder lift, elbow flex, wrist flex, wrist roll and gripper/trigger. The native angle is **90 degrees + the logical joint angle**. Do not edit the configured minimum/maximum bounds when changing a pose. ZERO is [0,0,0,0,0,0]; HOME is [0,-25,35,0,0,20] degrees. MID_RANGE is [0,0,0,0,0,35].

API drag probes did not reliably preserve the entire follower assembly and were discarded. Free mouse dragging is unverified; use the configurations or native mate controls. The controlled pose tests do not certify collision-free physical movement. In particular, isolated J2_MAX and J3_MAX follower poses penetrate the tabletop.

## Geometry and frames

The source's native Z-up frame is retained. The viewer's side-by-side X placement is removed. The CAD scene includes the source +2.4 mm tabletop placement; the URDF robot base omits that scene placement. `simulation/cad_rig.json` records the explicit transformation. The `SOURCE_Z_UP` view changes only the camera, not robot coordinates.

The follower forearm has three solid partitions. The leader base and forearm each have four. The leader forearm requires a disclosed 0.00001 mm internal numerical separation. Source zero-thickness artifacts are retained as labelled native sheets on the leader trigger and forearm; no physical thickness is invented. These are geometric preservation choices, not physical manufacturing validation.

## Evidence and simulator handoffs

Read `../docs/final_report.md`, `../verification/original_vs_solidworks.md`, and the machine-readable evidence in `evidence/` and `../verification/`. The ROS 2 package is under `../ros2_ws/src/so101_description/`. MuJoCo and Isaac handoffs are under `../simulation/`.

Physical mass, center of mass, inertia, actuator/contact properties and calibration remain unverified. The MuJoCo structural template deliberately refuses to infer physical inertias. ROS 2 visualization and Isaac import have not been run in this environment.

The faceted CAD is memory intensive. Open one robot assembly at a time if memory is limited. Build tools checkpoint mates and clear their undo history; saved checkpoints provide recovery. The MCP bridge is task-local stdio tooling in `tools/solidworks_mcp.py`, with no network listener or persistent installation.

## Supported pose tools

Use `tools/set_robot_pose.py` or the MCP `set_robot_joint_pose` tool for normal movement. `validate_real_limits.py`, `verify_master_assembly.py` and `audit_native_mate_connections.py` are verification tools. Reconstruction and `probe_*` scripts include historical rejected trials; they are not normal movement commands. In particular, do not use `add_configuration_pose_drivers.py`, the old `validate_leader_motion.py`, or raw component-drag probes on the delivered masters.

The main report is `../docs/final_report.md`; `../verification/deliverable_files.json` indexes delivered files separately from checkpoints.
