# Open issues and evidence boundaries

- Custom prints mostly preserve imported solid base geometry with native joint datums; fully parametric manufacturing feature histories were not recovered. Stock STEP is a different revision.
- The follower forearm has three solids; the leader base/forearm each have four. The leader forearm has a disclosed 0.00001 mm internal gap. Eleven native sheets retain zero-thickness source artifacts. Their physical manufacturing interpretation is unverified.
- Follower base and wrist pass the source 0.005 mm tolerance but fail the stricter 0.001 mm surface trial. Surface comparisons are sampled checks, not mathematical identity proofs. Leader per-part results are recorded separately.
- Accepted movement uses native mate solving and stored configurations. Failed follower drag and leader direct-dimension trials are rejected evidence. Free mouse dragging remains unverified. Use configurations and native mate controls.
- Calculated six-DOF constraint rank is not a SolidWorks kernel mobility diagnostic. Controlled native joint movement is separately measured.
- Software bounds do not establish physical stops or collision-free motion. Follower J2_MAX/J3_MAX and inherited leader poses penetrate the tabletop. Current discrete CAD checks and original L1 checks are distinct. Cables, swept clearance and physical fits remain unverified.
- Published assemblies omit spatial placement of some BOM fasteners and retention details. No unsupported screw placement, internal electronics or physical thickness was invented.
- Actual masses, COM, inertia, infill distribution, torque, speed, payload, backlash, friction, damping, compliance, contact, thermal and electrical behavior are unverified. Unit-density integrals are not physical material assignments. Generic servos are not verified genuine 55 g TowerPro units.
- Servo neutral/sign/horn indexing and AS5600 zero counts/sign/alignment/gap need physical calibration. Source defaults and HOME zero-capture conversion are documented, not physically validated.
- Concave print collision meshes are retained; accepted convex dynamic-contact proxies are outstanding. Servo primitive proxies were checked separately.
- Xacro/parser and MuJoCo forward kinematics are tested; physical dynamics are not. The MJCF template intentionally rejects loading without real inertias. ROS 2 build/RViz and Isaac import/USD were not run because their tools were not found in the accessible environment.
- Faceted CAD is memory intensive. Open one robot master at a time when memory is limited; preserve checkpoints before trying repairs or mate changes.

Engineering prototypes: not physically tested or payload rated. See final_report.md for quantitative results and physical validation requirements.
