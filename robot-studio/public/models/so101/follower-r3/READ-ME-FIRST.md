# SO-101 → MG996R follower R3

This is a **nominal-fit CAD assembly prototype**, derived from the exact
original SO-101 meshes. It is not a physically tested or payload-rated robot.
Use the seven files in `print-parts/`, or the P1S layouts in `plates/`.
Do not substitute stock SO-101 plates or mix the earlier R1/R2 parts into R3.

**Full-plate printing is not cleared yet.** Both plates generated G-code, but
plate 1 logged two slicer clipping errors. An independent coarse toolpath screen
also flagged 43 candidate missing cross-sections on plate 1 and 12 on plate 2.
Those candidates are not confirmed defects: the screen does not fully account
for holes, thin features or bridge-layer placement. They still require review.
The ZIP therefore contains the seven converted STLs and two **geometry-only**
3MF layouts, **not approved sliced projects or ready-to-run G-code**.
Do not start a full arm print just because the meshes are closed.

The passive encoder leader is a separate L1 kit: see `ENCODER-LEADER.md` in
the repository. Both ESP32 firmware roles are provided, but the follower ships
locked until physical calibration. Electronics housings are not included;
the website does not control hardware.

## What changed

- Six MG996R body cavities, mounting ledges and four slotted tab holes per motor.
- Six Ø20 mm metal-disc horn interfaces with four M3 holes on a Ø14 mm pitch circle.
- Joint-travel reliefs, rather than a zero-angle cavity alone.
- An 8 mm local extension between the wrist motors; joint placement moves with it.
- Base, shoulder and forearm fixed bracket pairs joined into single printing units.
  Their connection no longer depends on threaded holes in an STS3215 servo case.
- Straight underside access to the mounting nuts, and horn-screw head recesses.
- The obsolete WaveShare STS controller plate is excluded from the MG996R print kit.

The main links retain the source design. No whole-arm mesh scaling or unrelated
replacement robot is used. The forearm and shoulder brackets have documented
sub-0.1 mm local overlaps to turn tangential source seams into solid printed joints.
The source STLs and STEP files are preserved in the project, unchanged.

## Nominal hardware dimensions used

| Feature | CAD value |
|---|---|
| MG996R case, excluding shaft and tabs | 40.9 × 20 × 37 mm |
| Case bottom to shaft tip | 42.7 mm, TowerPro configure-table datum |
| Tab span / thickness | 54 / 2.6 mm |
| Case bottom to tab underside | 26.8 mm |
| Fixed case clearance | 0.3 mm per side |
| Tab-hole centre spacing | 49.5 × 10 mm, nominal assumption |
| Printed tab slots | 5 × 3.4 mm |
| Mount ledge | 4 mm |
| Metal horn option | 25T; Ø20 mm disc; 4 M3 holes on Ø14 mm PCD |
| Horn stack / printed mating plate | 4.5 / 6 mm |
| Purchased servo travel | User-confirmed 180°, positional |

The dimensions are nominal MG996R design inputs, as requested, not measurements
of the Amazon units. The Ø20 mm metal discs are a specified hardware option;
the plastic horns supplied in a servo box are not automatically interchangeable.
Use a horn that matches the actual spline. No plastic spline is printed.

Sources: [TowerPro MG996R](https://towerpro.com.tw/product/mg996r/) and
[the specified metal-disc drawing](https://www.handsontec.com/dataspecs/accessory/25T%20Servo%20Disc.pdf).

## Seven printed units

| Printing unit | Original source pieces incorporated |
|---|---|
| Base | Base_SO101 + Base_motor_holder_SO101 |
| Shoulder | Rotation_Pitch_SO101 + Motor_holder_SO101_Base |
| Upper arm | Upper_arm_SO101 |
| Forearm | Under_arm_SO101 + Motor_holder_SO101_Wrist |
| Wrist pitch/roll | Wrist_Roll_Pitch_SO101, locally extended 8 mm |
| Gripper body | Wrist_Roll_Follower_SO101 |
| Moving jaw | Moving_Jaw_SO101 |

Intermediate per-source files in the project are engineering intermediates, not
an alternate kit: use the seven joined printing units above.

## Prototype BOM

| Item | Quantity | Specification |
|---|---:|---|
| Positional MG996R | 6 | Four reported owned; two more for a complete follower |
| Matching metal disc horns | 6 | Ø20 mm, 25T option, four M3 tapped holes on Ø14 mm PCD |
| Horn centre-retaining screws | 6 | Correct screws for the servo shafts; use supplied matching screws, not an assumed M3 thread |
| Servo mounting screws | 24 | M3 × 12 mm, four per servo; nominal 2.6 mm tab and 4 mm ledge |
| M3 nuts | 24 | Standard 5.5 mm across flats; 6.8 mm access bores |
| M3 flat washers | 48 | About Ø7 mm, one under each mounting screw head and nut |
| Horn-to-printed-link screws | 24 | M3 × 8 mm, no extra washer in the modeled 6 mm plate + 2 mm thread-engagement stack |
| Printed units | 7 | The R3 kit, PETG |
| Desk clamps | 2 | Appropriate for the existing base and desk; clamp the base before a loaded test |
| ESP32 development board | 1 | Proposed controller; USB cable ×1 |
| PCA9685 PWM breakout | 1 | Six channels; 3.3 V logic with ESP32 |
| Regulated servo supply | 1 | 6 V, 10–15 A planning range; verify the actual units and wiring |
| Fused servo distribution and DC-rated cutoff | 1 set | Separate servo power path; common controller ground |
| Servo extension leads and signal wiring | 1 set | Route and choose lengths after the unpowered assembly |

No external follower encoders are required. The stock WaveShare STS serial-bus
controller is not the PWM driver for MG996Rs. A controller mounting enclosure,
cable clips and leader encoder BOM are not part of the printable R3 release.
Do not use the earlier custom robot's 2:1 firmware calibration on these direct-drive joints.

## P1S setup

Two geometry-only 3MF layouts contain the seven R3 units, with 12 mm between
part bounding boxes, a 35 mm front reserve and a 5 mm outer reserve.
They are candidates selected from 16 packing combinations, not a proof of the
globally fastest or minimum-plate solution.

Profile: Bambu P1S / 0.4 mm nozzle / textured PEI / generic PETG / 0.20 mm layers /
4 walls / 25% gyroid / automatic normal supports / 5 mm brim / print by layer.
The `plate-report.json` gives actual slicer outcomes and time/material estimates.
The current Arachne estimates are 10 h 46 min / 277.89 g for plate 1 and
9 h 8 min / 218.99 g for plate 2: approximately **19 h 54 min and 497 g PETG**
combined, including support/brim. These are provisional, not validated print
times or a guarantee of correct toolpaths. Inspect every layer in Bambu Studio,
especially screw ledges and horn plates, before a single-part fit print.
Sliced-file downloads remain withheld while the diagnostic review is unresolved.
Remove support from slots, body pockets, nut-access bores and horn holes before fitting.

## Assembly/test sequence

1. After reviewing its sliced layers, print and fit one mount first: the wrist
   pitch/roll or gripper unit can be selected individually in Bambu Studio. The earlier small
   body/tab gauge remains available separately, but is not a replacement arm part.
2. With power disconnected and the horn removed, insert each motor through the
   +shaft-side opening of its corresponding unit. Seat the tabs on the ledges.
3. Fit the four M3 mounting screws, washers and nuts. Nuts are accessed from
   beneath the ledges. Tighten evenly; do not crush the printed tabs or servo case.
4. Establish the servo's neutral position unloaded before final horn indexing.
   Disconnect power again before attaching a link. Never force a powered shaft.
5. Screw each metal disc to its driven printed plate using four M3 × 8 screws.
   The central opening provides access to the servo's own horn-retaining screw.
   Check real screw-tip clearance and thread engagement before tightening.
6. Work outward: base → shoulder → upper arm → forearm → wrist → gripper → jaw.
   Support the moving links during assembly. Check the complete unpowered travel,
   cable exits and access with the real fasteners before attempting a powered test.

## What the verification does—and does not—establish

The files are re-imported after export. Checks cover closed single-shell meshes,
nominal hornless insertion at 27 heights per joint, tab/horn screw passages and
material beneath the screw heads, plus 72 sampled robot poses. The JSON reports
record file hashes so changed geometry cannot inherit an old pass.

The collision report checks printed units and nominal servo/horn envelopes.
It does not model every fastener, wire, connector, screwdriver or manufacturing
tolerance. It is sampled, not a continuous-motion proof. Some combinations of
otherwise valid joint angles go through the tabletop; the website's slider guard
does not constitute a hardware safety controller.

**This prototype relies on the MG996R's single-sided output support.** Stock
STS rear-idler geometry is relieved where the larger case needs space; no invented
rear shaft is shown. Shaft/bearing loads, PETG stiffness, torque and temperature
need bench testing. No payload or continuous-duty rating is assigned. Full-reach
gravity loads may require counterbalancing; published stall torque is not a usable
continuous torque specification. Keep the arm supported for initial tests.

Neither a closed STL, a collision-free sampled pose nor successful slicing proves
that the assembled powered robot works. The leader encoder conversion remains separate work.
