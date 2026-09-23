# Reconstruction status

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
