# Print this first — unpowered MG996R fit test R1

**Do not print the entire arm.** This checks your purchased MG996R and tabs against
nominal dimensions. It does not validate motion, strength, payload or bearings.

## Files

- output/fit-test-r1/P1S_QUICK_GAUGES_ONLY.3mf: fast first print, two gauges.
- output/fit-test-r1/P1S_FIT_TEST_ONLY.3mf: wrist-holder prototype plus those gauges.
- Individual STL and editable STEP files are in the same folder.
- BENCH_FIT_ASSEMBLY.step: nominal servo inserted into holder, reference only.
- MG996R_REFERENCE_DO_NOT_PRINT.stl: purchased hardware envelope, do not print.
- verification.json: exported-mesh, nominal fit and slicing checks.

These plates are alternatives/stages, not two required full plates. Print the quick
gauges first. If they fit, remove the already printed gauges from the full 3MF and
print just the holder, retaining its supplied orientation. Scale stays **100%**.

## P1S setup and estimates

Sliced for P1S **0.4 mm nozzle**, Generic PETG, Textured PEI, 0.20 mm layers,
4 walls, 25% gyroid, automatic normal supports and 5 mm outer brim. Open the 3MF
in Bambu Studio, confirm your actual filament/printer/nozzle, inspect supports in
layer view and re-slice before sending. Do not send these profiles to a differently
configured printer.

Approximately **18 minutes / 5 g** for gauges; **1 hour 28 minutes / 24 g** for the
full test plate. Exact current estimates are in verification.json. Physical results
vary. All three parts fit one plate, clear of the front-left exclusion region.
This is not a claim of global minimum print time.

## What changed in the holder

The starting solid is the exact Motor_holder_SO101_Wrist.step. Original shape is
retained where possible. Added local material makes the two tab supports; body
opening has **0.30 mm nominal clearance per side**. Four elongated M3-clearance
slots allow small adjustment around assumed 49.5 × 10 mm hole centres. The tab
seating plane retains the nominal shaft datum. Underside bores provide nut access.
An approximately 16.34 mm³ severed shaving from the old cavity was deliberately
removed. The result is one valid solid and one watertight STL.

**BENCH ONLY:** it has not passed full-arm fit/collision checks. Its original
opposite-side support interface is still unconverted.

## Unpowered test procedure

1. Disconnect the servo completely. Remove the retaining screw and lift off its
   horn without forcing the shaft. Keep the original screw.
2. Deburr the gauge and remove brim/support residue. Do not enlarge it to turn a
   failed fit into a pass. Record any sanding separately.
3. Pass the body through the rectangular gauge until tabs rest on it. Check body,
   four hole locations and wire exit. The 41.5 × 20.6 mm opening tests the body
   section, not shaft height.
4. If it fails, stop; measure the obstruction, body and tab pitch. Do not force it
   or print the holder yet.
5. If it passes, insert the servo into the holder from the open tab side, horn
   removed, cable clear. It should insert and remove without force.
6. Try four M3 × 12 screws, washers and nuts only if actual tab holes accept M3.
   Tighten only enough to seat tabs: no crushing or visible flange bending.
   Confirm nut access and that screw tips do not contact the case.
7. The optional round gauge has four Ø3.4 mm holes on a 14 mm pitch circle for
   the proposed disc horn. A different supplied horn does not mean a bad servo;
   report its actual pattern so the interface can be adapted.
8. Photograph above, both ends and wire-exit side with a ruler/caliper visible.
   Return measurements below. **Do not power this prototype or attach arm links.**
   Powered travel follows complete mechanical interfaces and safe stops.

## Measurements to return

| Measurement | Nominal used / actual to fill |
|---|---|
| Case L × W × H, excluding shaft | 40.9 × 20 × 37 mm / ______ |
| Tab end-to-end span | 54 mm / ______ |
| Tab thickness | 2.6 mm assumed / ______ |
| Case bottom to tab underside | 26.8 mm assumed / ______ |
| Tab hole pitch, long × short axes | 49.5 × 10 mm assumed / ______ |
| Tab hole diameter | Must accept selected screw / ______ |
| Shaft centre from nearest case end | 10 mm assumed / ______ |
| Case bottom to fitted horn link-contact face | 47.2 mm assumed / ______ |
| Supplied horn diameter, holes, pitch, thickness | Unconfirmed / ______ |
| Gauge fit without sanding | pass / tight / loose / fails |
| Insertion, cable, screw/nut access | pass / obstruction location ______ |

Your reported 180° travel is recorded. The preview's ±80–85° ranges are not a
physical calibration. After mechanical approval, establish centre and safe
endpoints unloaded; do not start by commanding the advertised endpoints.

## Checks passed and limits

The holder is one valid BREP solid; all three printable STLs are single watertight
positive-volume shells. Exact intersection with the **nominal** servo is zero.
The defined top insertion envelope and four underside nut-access bores are clear.
Both alternative plates slice successfully with the stated profile.

These checks are not measurements of your hardware, structural analysis,
assembly-wide motion testing or a physical print/bench test. See BOM.md for
test hardware and the provisional follower/leader shopping list.

