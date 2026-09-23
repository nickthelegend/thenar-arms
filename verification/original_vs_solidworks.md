# Original versus SolidWorks

The accepted follower reconstruction preserves the current modified R3 revision. Stock upstream STEP files describe a different revision and were not substituted for it. The source dimension register is in ../docs/source_audit.md. Native servo/horn sketches reproduce the nominal project primitives; custom printed geometry remains imported solid base features with native joint datums, not recovered manufacturing feature histories.

All 11 solid bodies in nine unique follower components report zero SolidWorks kernel faults. The forearm uses three closed, nonoverlapping solid partitions in one rigid part; its source seam prevents a successful native single-body union. Its original failed surface is suppressed and retained for traceability.

Printed exterior comparison includes all mesh vertices and 30,000 surface samples in each direction (50,000 for the forearm). Largest observed exterior discrepancy is 0.001958407 mm on the base; wrist reaches 0.001701408 mm. Both miss the stricter 0.001 mm trial check. All seven fit the 0.005 mm simplification tolerance used by the source generator. The forearm exterior comparison is below 0.000272 mm. These are bounded sampled comparisons, not mathematical identity claims. See printed_surface_comparison.json and ../solidworks/evidence/Forearm_seam_comparison.json.

All 19 component transforms were measured after native mate solving in 28 poses: each joint minimum, zero, maximum and return, plus HOME and a multi-joint pose. Maximum component-position difference from source forward kinematics is below 0.000001 mm; maximum orientation difference below 0.000001 degree. Joint axis origins remain within 0.000001 mm. Datum sketch endpoints were read back within 1e-11 m. Saved ZERO, HOME and MID_RANGE configurations were independently read back and passed.

This checks link spacing, joint locations, axes, signs, servo and horn placements, and gripper motion through the recorded poses. Detailed holes and interfaces are covered by exterior sampling and the source dimension register; they have not all been reverse-dimensioned into editable sketches. The six native hinge chains contain axis-collinearity and axial-location mates, with source limit-angle mates; twelve hardware lock mates attach hardware to its correct rigid group. Only the base is grounded.

Native SolidWorks HOME interference and 15 independent CAD-mesh pose checks report the six source-intended shaft/horn engagements, approximately 9.032 mm3 each. No other sampled internal overlap exceeds the source 0.5 mm3 threshold. J2_MAX and J3_MAX at other joints zero penetrate the tabletop. Discrete sampling does not certify swept or physical motion.

URDF/Xacro passes parsing, connected-tree, units/path and 28-pose comparison checks. MuJoCo URDF-import forward kinematics also passes all 28 poses. Its automatically inferred masses are rejected. Physical mass, COM, inertia, actuator/contact data and validated convex print proxies remain incomplete. ROS 2 visualization and Isaac import were not run in this environment.

Direct API drag probes failed and were discarded; HOME was rebuilt from a valid ZERO configuration and all saved configurations reverified. Manual use should currently rely on named configurations and native mate-angle controls. Mouse-drag behavior remains unverified.

## Leader L1 adopted geometry

All 18 adopted native-file exports pass their recorded comparison gates. Largest sampled bidirectional source/CAD discrepancy is 0.003381282 mm; individual bounds, volumes and stricter 1 µm checks are in `leader_geometry_comparison.json`. There are 25 healthy solid bodies across the unique components and 11 healthy source-artifact surface bodies. Base/forearm solid partitions and the 0.00001 mm forearm internal separation are disclosed numerical preservation measures.

The separate leader master contains 73 instances, one fixed base and 90 total native mates (84 active in FREE_MOTION). All 28 measured poses pass, maximum component position difference 5.80356045e-07 mm and orientation difference 3.86665823e-10 degrees. All three stored configurations pass final readback. The same six logical joints map through six AS5600 channels to the follower, with the source 14 mm wrist extension and +15 degree trigger mesh index retained.

Current leader volumetric collision checks use actual individually exported CAD solid bodies at 15 measured poses. Their pairwise results and table penetrations are in `leader_cad_mesh_motion_interference.json`; source zero-thickness surfaces are excluded only from solid-volume intersections. The inherited source 72-pose report remains separate. These are discrete checks, not collision-free swept-motion certification.

Both assembly constraint graphs calculate six independent rotations at HOME, with no additional infinitesimal freedom. This is a mathematical topology check, not freehand-drag verification. Failed drag/direct-dimension trials are rejected evidence. See `../docs/final_report.md` for the complete acceptance scope.
