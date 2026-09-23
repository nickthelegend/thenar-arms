# Reconstruction source audit

Current target: SO101-MG996R follower R3 and passive AS5600 leader L1. Engineering prototypes, not physically tested or payload rated.

## Authority and revision

No original parametric CAD, SLDPRT, SLDASM or FCStd is present in the supplied project. Fourteen upstream STEP solids exist, but these are the STOCK geometry. The current R3/L1 modifications were performed on the upstream STL meshes with manifold3d, not on those STEP solids. Substituting stock STEP geometry would discard current mounts, travel reliefs, seam overlaps and wrist extensions. The R3/L1 generator code plus its hash-identified released meshes and assembly transforms are the authority for the CURRENT revisions. Historical R1/R2/clearance STEP files are not current R3 parts. No geometry averaging is permitted.

The audit inventories and hashes every original file, reads text sources into a searchable line index, inventories ZIP/3MF contents, and measures every used published mesh. Binary source files are preserved. These checks do not establish native feature reconstruction or physical fit. See verification/source_geometry.json and solidworks/checkpoints/original_files_sha256.json.

## Dimensional register

| Quantity | Value | Units | Source | Classification / conflicts |
|---|---|---|---|---|
| MG996R case | 40.9 × 20 × 37 | mm | R3-PRINT.md; build_follower_r3.servo | SOURCE VERIFIED nominal input; purchased hardware unmeasured |
| Case bottom / top | -28.5 / 8.5 | mm local servo Z | build_follower_r3.servo | SOURCE VERIFIED |
| Shaft centre | 12.5, 0 | mm local servo XY | build_follower_r3.cyl | SOURCE VERIFIED |
| Shaft tip | 14.2 | mm local servo Z | build_follower_r3.servo | SOURCE VERIFIED; historical clearance model differs |
| Tab span / width / thickness | 54 / 20 / 2.6 | mm | build_follower_r3.servo | SOURCE VERIFIED nominal |
| Tab holes / slots | 49.5 × 10 / 5 × 3.4 | mm | R3-PRINT.md; slots() | SOURCE VERIFIED nominal |
| Metal disc / hole PCD | 20 / 14 | mm | metal_horn() | SOURCE VERIFIED option, actual horn UNVERIFIED |
| Metal-disc holes | 2.5 | mm | metal_horn() | SOURCE VERIFIED tap-drill envelope; M3 threads unmodelled |
| Printed horn holes / centre bore | 3.4 / 6.4 | mm | horn_plate() | SOURCE VERIFIED |
| Horn stack / driven plate | 4.5 / 6 | mm | metal_horn(); horn_plate() | SOURCE VERIFIED |
| Follower wrist extension | 8 | mm | R3 generator + manifests | SOURCE VERIFIED; do not use stock/R2 geometry |
| Leader wrist extension | 14 | mm | L1 generator | SOURCE VERIFIED; differs deliberately from follower |
| Shoulder seam overlap | 0.031, -0.047, 0.029 | mm | R3 generator | SOURCE VERIFIED local translation |
| Follower forearm seam overlap | 0, -0.05, 0 | mm | R3 generator | SOURCE VERIFIED local translation |
| Adafruit6357 board | 25.4 × 17.78 × 1.6 | mm | Eagle + L1 source | Outline SOURCE VERIFIED; thickness ASSUMED in source |
| PCB holes | ±10.16 × ±6.35; diameter 2.5 | mm | Eagle + L1 source | SOURCE VERIFIED |
| Bearings | 8 × 16 × 5 | mm | ENCODER-LEADER.md; L1 source | SOURCE VERIFIED nominal 688ZZ |
| Bearing pocket / journal | 16.3 / 7.95 | mm | cartridge_parts() | SOURCE VERIFIED |
| Magnet / pocket | diameter 6 × 2 / diameter 6.2 | mm | cartridge_parts() | SOURCE VERIFIED nominal |
| Magnet-to-chip gap | 2 | mm | L1 report + source | SOURCE VERIFIED nominal; field strength UNVERIFIED |
| Leader trigger indexing | +15 | deg | L1 context() | SOURCE VERIFIED revision correction |
| Follower joint origins | six complete matrices | mm / degrees | published manifest | SOURCE VERIFIED; copied to simulation/joint_map.yaml in SI |
| Home | 0, -25, 35, 0, 0, 20 | deg | model.h + manifest | SOURCE VERIFIED; differs from ZERO |
| Preview/command limits | ±85, ±80, ±80, ±80, ±85, 0–70 | deg | model.h + manifest | SOURCE VERIFIED software limits, NOT physical travel certification |
| Direct drive ratio | 1:1 | ratio | model.h + R3 guide | SOURCE VERIFIED; historical custom-arm 2:1 is excluded |
| Display base separation | 800 | mm | publisher/viewer | Display only; remove ±400 mm X shifts for separate robot assemblies |

## Coordinates and mechanism

Source position values are millimetres; source rotations use intrinsic XYZ Euler degrees (Three.js XYZ). Each fixed joint datum is followed by an independent local Z rotation. Converting these rotations to URDF requires matrix conversion to extrinsic xyz RPY radians, not copying the Euler triples. Native SolidWorks assembly convention will retain source world axes with Z up. Separate assemblies remove only viewer root X offsets; the 2.4 mm vertical root placement is explicit. ROS base_link convention retains original URDF frame and needs an explicit ground offset of 2.4 mm when used with a table.

The sixth follower actuator rotates one moving jaw directly; the opposite gripping surface is part of Gripper_body. There is no evidence of a paired-jaw linkage, gear reduction, or parallel-jaw translation. Horns belong to child links, servo bodies to parent links. Leader rotor, magnet cup and magnet belong to child links; cartridge, caps, boards and bearing envelopes belong to parent links.

## Conflicts and unknowns

The original URDF includes STS3215 mass/inertia and limits. They cannot be reused for the modified MG996R/PETG robot. Physical servo signs, horn indexing, travel and pulse slopes are uncalibrated defaults. Materials/infill and purchased component masses do not establish assembled mass/inertia. Keep unknown dynamics UNVERIFIED.

Existing follower report: 72 discrete poses internally clear at its 0.5 mm³ threshold, eight table-intersection poses. Existing leader report: two folded internal collisions, eleven table-intersection poses. These are inherited source reports, not new SolidWorks tests, and they do not certify swept motion. Preserve known collisions without redesigning geometry.
