# SO-101 original-geometry MG996R conversion work

## New: passive encoder leader L1

The original-derived leader conversion is now in `output/encoder-leader-l1`:
37 pieces on three P1S geometry layouts. See [ENCODER-LEADER.md](ENCODER-LEADER.md)
for the complete BOM, verified nominal interfaces, wiring, firmware and remaining
physical tests. The current viewer shows both converted assemblies. Full-plate
slicer clearance is still pending; these are not ready-to-run G-code files.

## Current: original-derived MG996R follower R3

The actual converted kit is now in `output/follower-r3/print-parts`: **seven
joined printing units**, derived from the original SO-101 parts. It has six
MG996R tab mounts, six metal-disc horn interfaces, joint-travel reliefs and an
8 mm local wrist extension. Use [R3-PRINT.md](R3-PRINT.md) for its current BOM,
dimensions and assembly notes. Do not mix R1/R2 parts or fasteners into this kit.

- Seven exported units are closed, positive-volume, single-shell meshes.
- All six nominal insertion and tab/horn screw-land checks pass.
- No internal overlaps above the report's threshold in 72 sampled poses;
  eight poses intersect the table and are guarded in the viewer.
- Two P1S geometry layouts hold all seven units with 12 mm part spacing.
- **Slicing review is still open:** both plates generated G-code, but clipping
  diagnostics and coarse toolpath-screen candidates remain. Ready-to-run sliced
  files are withheld. Full-plate printing is not approved by these checks.
- Physical fit, single-sided shaft support, strength, payload, cables and powered
  operation remain untested. Encoder leader L1 is supplied separately above.

The website defaults to this R3 follower. `?geometry=original` explicitly opens
the stock reference. `?geometry=clearance&view=fit-test` now shows the actual R3
layouts, not the earlier test-only or original SO-101 plates.

Download: [R3 prototype ZIP](output/follower-r3/SO101-MG996R-R3-PROTOTYPE.zip).
The sections below preserve earlier development results; they are **historical**
and do not describe the current R3 follower or its checks.

## Historical: printable MG996R bench-fit prototype R1

See [FIT-TEST.md](FIT-TEST.md) and [BOM.md](BOM.md). Actual original-derived
wrist-holder test STL/STEP and two small gauges are in `output/fit-test-r1`.
The holder adds mounting ledges, screw slots, nut access and an insertion opening.
It is one valid solid, with zero nominal servo overlap; all three test meshes
are watertight. This is separate from the incomplete full-arm study below.

P1S / 0.4 mm / PETG slicing passed: quick gauges approximately 18 minutes and
5 g; holder plus gauges approximately 1 hour 28 minutes and 24 g on one plate.
Print the quick gauges first. **Unpowered bench fit only; not a complete arm.**
The website's Print plates view now includes these test prints before the stock
SO-101 layouts. `?geometry=clearance&view=fit-test` opens them directly.

## Wrist-spacing development R2 — still not a print release

`output/wrist-spacing-r2` contains an editable original-derived wrist part with
an 8 mm local section extension. No global mesh scaling was used. With the roll
servo/gripper shifted accordingly, the two nominal wrist servo envelopes have
zero positive-volume interference in 81 pitch samples from -80° to +80° in 2°
steps; minimum sampled separation is approximately 2.566 mm. A 4 mm shift was
insufficient. This is a servo-pair test, NOT a complete assembly motion check.

The extension and clearance-cut STEP are each valid single solids, but the R2
STL still has open seams. An automatic repair was rejected because its volume
differed from the STEP by approximately 0.243%, exceeding the 0.1% repair gate.
R2 is intentionally not in the print-test ZIP or presented as printable. Flange,
horn, opposite-side support and surrounding-link checks remain incomplete.
The existing whole-arm report and viewer were not silently altered by this work.

## Historical initial study — NOT an MG996R print kit

All 14 requested individual STLs and both Ender combined layouts were downloaded
from TheRobotStudio/SO-ARM100 at commit
`eecbe3e0a9ebb23e25ad7b2759b03884c6660903`. They are byte-for-byte identical to
the same revision in the workspace. `source/provenance.json` records download
URLs, SHA-256 hashes, dimensions and mesh checks. Original files are unmodified.
The matching original STEP files are in `source/STEP`. Upstream Apache-2.0
licensing is preserved in `source/LICENSE`.

The website now renders these original shapes, not the earlier custom arm.
Follower joint frames come from the upstream URDF. The original leader handle
shares the wrist housing's mounting coordinates; its trigger pose is provisional.
Joint motion is a geometric preview, not a collision or hardware test.

## Historical initial verification and viewer update

The user has confirmed that the purchased servos only travel 180 degrees.
The MG996R preview now uses provisional ranges of ±85°, ±80°, ±80°, ±80°,
±85°, and 0–70° respectively. These are inspection limits, NOT mechanically
validated operating limits. The original-reference view retains upstream limits.
The two bases are separated by 800 mm for display only; no STL dimensions changed.

`output/motion-verification.json` records a 44-pose CAD check: home, neutral,
18 single-joint min/mid/max poses, 16 motion-demo samples and 8 seeded combined
poses. All 44 contain unresolved positive-volume overlaps in the nominal model.
There are seven home-pose candidates, including approximately 1,092 mm³ between
the unchanged wrist motor holder and the nominal MG996R envelope. Two draft
STLs still have open seams: Motor_holder_SO101_Base and Wrist_Roll_Pitch_SO101.
The check includes conservative circular horn envelopes, so the exact pair and
assumed hardware must be reviewed before deciding a repair. It does not certify
continuous swept motion, minimum clearance, leader encoders, strength or payload.

The website displays the report and lets you select its sampled poses. The
software tests verify that all twelve displayed joints move their attached
geometry, transforms remain finite, input is clamped, and the two display
assemblies do not overlap at home. These are software checks, not physical tests.

**Do not print the draft conversion as a finished arm.**

## Purchased servo — user-reported 180-degree travel

The user purchased a four-pack from
[Amazon ASIN B0F2TKPB95](https://www.amazon.in/dp/B0F2TKPB95).
The page was inspected on 2026-09-17. It identifies Generic / TESTIN ELECTRONICS,
not a verified TowerPro product. Its title advertises 180-degree operation, but
the description, included-components field and box contents describe a
360-degree continuous-rotation version. A verified buyer reports receiving
continuous-rotation servos. Those statements do NOT establish what the user
actually received; the page is internally inconsistent. The user's subsequent
confirmation of 180-degree travel is now recorded in `purchased-hardware.json`.

This distinction is essential: a positional servo accepts a target angle;
a continuous-rotation servo normally accepts speed/direction. Continuous-rotation
units cannot perform this arm's requested angle positioning without external
feedback or different servos. The user explicitly requested NO external arm
encoders, so adding them is not an approved workaround.

Before final calibration, test one servo off the robot with the horn
unloaded, using a servo tester and an appropriate separately powered supply.
Move the control slightly to either side of neutral: does the shaft move to a
new position and hold, or keep turning? Do not force the shaft by hand to test
travel. Do not power a servo from a microcontroller's GPIO or 3.3 V rail.
Stop if it stalls, overheats or behaves unexpectedly.

The listing's rounded 40 × 40 × 20 mm dimensions are not a machining drawing.
The supplied horn hole pattern, tab pitch and actual shaft datums remain
unmeasured. The fit study uses nominal MG996R geometry, NOT confirmed dimensions
of this Amazon product. Its nominal 20 mm metal horn is an assumption, not a
claim about the horn kits supplied with this purchase.

The follower needs six positional servos including the gripper. If only one
four-pack was purchased, two further matching units would eventually be needed;
confirm the existing units before buying any more.

## What was actually generated

- `source/Individual`: all 14 exact source STLs.
- `source/Follower` and `source/Leader`: both original Ender combined STLs.
- `source/STEP`: original editable solids, not reverse-engineered approximations.
- `output/manifest.json`: original-part assembly transforms for the viewer.
- `output/clearance-study`: localized subtractive fit-study STEP/STL exports,
  nominal MG996R reference mesh, and a per-part interference/removal report.

The fit study never scales or replaces the arm. It subtracts nominal servo,
horn and provisional cable-clearance envelopes at original joint locations.
It does NOT yet create a complete load-bearing attachment system. Some draft
tessellations have open seams; consult `fit-analysis.json`. These are inspection
artifacts, not print-ready parts. Watertightness alone would not establish
mechanical compatibility or strength.

The wrist motor holder clearance cut produces TWO separate solids and is
rejected. No converted wrist motor holder STL is exported. The wrist roll/pitch
part loses approximately 21.6% of its volume under the current assumptions,
which makes wall thickness and load paths especially important to review.

Four unaffected or leader-only files are preserved unchanged in the study
package. A draft suffix on them does not mean an encoder conversion was done.
The leader remains the original reference; AS5600 cartridges have not been
designed in this original-design branch.

## P1S layouts

The original Ender follower layout and original Ender leader layout each fit
inside a P1S 256 × 256 × 256 mm envelope after rigid translation only. Neither
the original orientations nor mesh scale is changed. Each layout occupies one
plate, with Y > 35 mm and X > 19 mm, clear of the front-left exclusion rectangle.
The website offers geometry-only 3MF layouts and the untouched combined STLs.

These are STOCK SO-101 plates, not MG996R plates. They are not sliced toolpaths.
No minimum-time claim, support approval, or MG996R print-time estimate is made.
Do not print them expecting the purchased MG996Rs to fit.

## Remaining engineering sequence

1. Calibrate the usable angle range and horn indexing of the reported 180-degree servos.
2. Measure body L/W/H, overall height, shaft offset, tab span/thickness/height,
   hole pitch and diameters, and the included horn hole pattern and stack height.
3. Register those measured datums to the original SO-101 joint axes.
4. Complete local tab mounts, horn attachment and opposite-side idler support;
   repair the rejected wrist mount while retaining the original design.
5. Check minimum walls, fastener access, cable bend paths and swept interference.
6. Evaluate direct-drive shoulder/elbow torque, current and heating. No payload
   is rated; published stall torque is not a continuous working torque.
7. Print and bench-test a single joint. Correct tolerances before full plates.
8. Fit passive encoder cartridges into the original leader housings.
9. Arrange only approved parts for P1S, slice, inspect supports and measure times.

The earlier `mg996r-arm` custom design and firmware are retained for history but
are NOT the authority for this requested original-design conversion. In
particular, its 2:1 transmission calibration must not be used for this branch.

## Reproduce

From the workspace root:

```sh
mg996r-arm/.venv/bin/python so101-mg996r/tools/import_sources.py
mg996r-arm/.venv/bin/python so101-mg996r/tools/clearance_study.py
mg996r-arm/.venv/bin/python so101-mg996r/tools/verify_motion.py
cd robot-studio
node scripts/verify-preview.mjs
npm run dev -- --host 127.0.0.1
```

The local site is normally at http://127.0.0.1:5173/.
Use its geometry selector for Original SO-101 versus MG996R clearance study.
Do not overwrite the source files with draft exports.
