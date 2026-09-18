# SO-101 passive AS5600 encoder leader · L1

**Nominal assembly prototype, not physically validated.** This kit converts the
original SO-101 leader links, handle and trigger to six passive encoder joints.
It does not put encoders on the MG996R follower. Do not use stock SO-101 plates
or mix L1 leader parts with R3 follower brackets.

## Files and plates

`output/encoder-leader-l1/print-parts/` contains seven main printing units:
Base, Shoulder, Upper_arm, Forearm, Wrist_pitch_roll, Handle and Trigger,
all ending `_Encoder_L1.stl`. Print one each.

Print **six each** of `Encoder_cartridge_L1`, `Bearing_cap_front_L1`,
`Bearing_cap_rear_L1`, `Encoder_rotor_L1`, and `Magnet_cup_L1`.
Total: **37 pieces, 12 unique files, three P1S geometry-only 3MF layouts**.
The MG996R follower adds seven pieces on two plates: five layouts for both.
Only files listed in the reports/ZIP are kit parts; engineering intermediates
and diagnostic candidates are not alternate print files.

Packing tries 16 rectangle-packing variants, with 12 mm part spacing, a 35 mm
front reserve and 5 mm outer clearance. This is not a proven minimum print time.
Starting settings: P1S, 0.4 mm nozzle, PETG, 0.20 mm layers, four walls, 25%
gyroid, automatic supports and 5 mm outer brim, printing by layer.
**Geometry layouts are not print-approved G-code.** Inspect all sliced layers,
especially bearing shoulders, rotor pockets and support removal. See
`plate-report.json` for actual slicer results. Full-plate release is withheld
while slicer clipping diagnostics/layer review remain unresolved.

Start with ONE five-piece cartridge set, not the complete plates.
Use the separate `test-first/P1S_ENCODER_CARTRIDGE_FIT.3mf` in the ZIP for this;
it is an optional preliminary print, not a fourth full-kit leader plate.
This test layout sliced without logged errors: estimated 1h19m, 25.41 g PETG.
Full leader layouts estimate 27h34m and 671.04 g, including supports/brims with
the recorded settings; plates1–2 log clipping errors. Estimates are not measured
print times or permission to skip layer inspection.
Keep support
scars out of the bearing seats. Check the 7.95 mm journal and 16.3 mm bearing
pocket with your printer/material. Sand lightly if needed; never force bearings
into brittle or undersized prints. Reject cracked or loose load-bearing parts.

## Complete incremental leader BOM

| Item | Qty | Required specification |
|---|---:|---|
| AS5600 breakout | 6 | **Adafruit 6357** geometry; generic AS5600 boards are not interchangeable |
| Bearings | 12 | **688ZZ, 8 × 16 × 5 mm**; not the 4 mm-wide open bearing variant |
| Magnets | 6 | Ø6 × 2 mm, **diametrically** magnetized; axial magnets will not work |
| Main printed units | 7 | One of each original-derived L1 unit |
| Cartridge printed pieces | 30 | Six of each of the five reusable parts |
| Cartridge mounting bolts | 24 | M3 × 12, four per joint |
| Rotor-to-link bolts | 24 | M3 × 12, four on Ø14 mm PCD per joint |
| Axle retainers | 6 | M3 × 35 countersunk; verify actual head size and protrusion |
| M3 nuts | 54 | 24 mounting + 24 rotor + 6 axle; standard 5.5 mm AF |
| M3 washers | 48 | Approximately Ø7 mm, both sides of mounting tabs |
| Bearing cap screws | 24 | M2 × 6, into printed pilot holes, do not over-tighten |
| PCB screws | 24 | M2 × 4, into printed pilots; verify engagement without crushing PCB |
| ESP32 development board | 1 | Classic ESP32 target, USB cable ×1 |
| TCA9548A breakout | 1 | Address 0x70, logic and pull-ups at 3.3 V |
| Flexible sensor leads | 6 sets | Four conductors each; strain relief/service loops at every axis |
| Desk clamps | 2 | Suit original base and your desk |
| Magnet adhesive | as needed | Retain magnet in cup; keep adhesive out of bearings |

Use an additional ESP32/PCA9685 for the follower: see [R3-PRINT.md](R3-PRINT.md).
Add a **10 kΩ pull-up from PCA9685 OE to 3.3 V**, connect OE to follower GPIO25.
A hardware servo-power disconnect, suitable regulated servo supply, common
ground and wiring/fusing sized for the actual motors are required. Do not power
six servos from USB or the ESP32. No final current/load rating is established.
No electronics enclosure or exact ESP32/mux/PCA board mounting model is supplied:
those board variants have not been selected. Reference meshes are not electronics
to print. Only the AS5600 board is geometrically specified.

## Dimensions and retained design

The original SO-101 link geometry is locally cut/extended, not globally scaled.
The leader wrist is extended 14 mm. Handle and its fixed wrist bracket are joined.
The trigger mounting face is corrected and indexed +15° to avoid its original
misregistered position. Tiny documented seam overlaps join tangent source meshes.

| Interface | Nominal CAD value |
|---|---|
| AS5600 board | 25.4 × 17.78 mm; 1.6 mm thickness assumed |
| Four PCB hole centres | ±10.16 × ±6.35 mm from sensor centre; holes Ø2.5 |
| Bearing pockets / journal | Ø16.3 / Ø7.95 mm |
| Cartridge tab span / thickness | 64 / 2.6 mm |
| Four cartridge holes | 55.5 × 10 mm spacing; Ø3.4 |
| Printed rotor disc | Ø20 mm; four M3 holes on Ø14 PCD |
| Magnet pocket | Ø6.2 mm, adhesive retained |
| Magnet bottom to chip top | 2.0 mm nominal; field strength must be tested |
| Output travel limit | ±85°, ±80°, ±80°, ±80°, ±85°, 0–70° |
| Calibration home | 0°, −25°, +35°, 0°, 0°, +20° |

The cartridge is a printed shaft/journal design reinforced by an axial M3
retainer, not a machined precision shaft. Bearing preload, play and durability
are bench-test questions. The reference PCB includes conservative connector
envelopes, not every solder fillet/component height.

## Assembly order (unpowered)

1. Print one cartridge set. Trial-fit both bearings and cap screws. Clean the
   through-bores; check the rotor turns freely without caps rubbing it.
2. Slide the AS5600 PCB into the lower frame, component side toward the magnet.
   Attach its four M2 screws. Fit leads through side openings before closing it.
3. Fit the rear bearing and rear cap, then the front bearing. Insert the rotor
   through the bearings; install the front cap. Capture the four rotor M3 nuts
   and the central axle nut in their pockets before attaching the link.
4. Engage the magnet cup's hex socket with the rear rotor key; install the axial
   M3 retainer through the cup into the rotor nut. Do not preload the bearings or
   let the screw protrude into a mating part. Confirm free rotation and low play.
5. Glue the diametric magnet into the cup with its bottom at the modelled datum.
   Check the AS5600 status and stable angle readings through a complete rotation.
   Strong/weak/missing magnet status is a failed test, not a software workaround.
6. Once that test passes, print the rest. Build base → shoulder → upper arm →
   forearm → wrist → handle/trigger. Install each cartridge with four tab bolts,
   nuts and washers, then attach its driven link with four rotor bolts. Confirm
   real fastener/tool access and engagement at each stage before enclosing it.
7. Clamp the base. Add flexible cable loops and strain relief; move every joint
   by hand through its restricted range. Stop at interference or cable tension.
   Avoid combined folded poses that hit the base/table. Calibrate before any
   follower connection. No unrestricted 360° arm motion is intended.

## Wiring and firmware

Leader: ESP32 3V3 → mux VCC and six sensor VINs, common GND; GPIO21 → SDA,
GPIO22 → SCL on mux upstream. Mux A0/A1/A2 low (0x70), reset held high per its
board instructions. Connect one AS5600 to each channel 0–5, in joint order above.
The sensors all use address 0x36; firmware selects only one mux channel at once.
Keep I²C leads short, flexible and away from servo power; firmware uses 100 kHz.

Follower: separate ESP32 GPIO21/22 → PCA9685 SDA/SCL, VCC=3.3 V, address0x40.
GPIO25 → OE plus the external pull-up. Servo signals use channels0–5; servo
power is a separate regulated rail with common ground. Disconnect power before
rewiring. OE disables PWM, **not motor power or gravity**: support the arm and
provide a physical power-disconnect switch.

```sh
arduino-cli compile --fqbn esp32:esp32:esp32 --build-property compiler.cpp.extra_flags=-DROLE_LEADER=1 so101-mg996r/firmware/thenar
arduino-cli compile --fqbn esp32:esp32:esp32 --build-property compiler.cpp.extra_flags=-DROLE_LEADER=0 so101-mg996r/firmware/thenar
```

Both roles were compiled with ESP32 core3.3.10. Nothing was flashed or hardware
tested. Serial115200. Leader initially sends `RAW`; place it at displayed home
and send `ZERO`. Check each axis direction, using `SIGN 0 -1` etc. as required;
zeros/signs persist. `FORGET` clears calibration. Valid output is `L q0 … q5`.

Follower firmware ships **locked** (`FOLLOWER_CALIBRATED=false`). Bench-calibrate
each real servo's centre, direction, usable endpoints and pulse slope in
`calibration.h`, with horns disconnected first; only then enable the flag.
The mapping is 1:1 direct drive, not a 2:1 reduction. A claimed 180° servo is not
assumed safe over every pulse width. Re-index horns at the prescribed home.

```sh
python -m pip install numpy pyserial
python so101-mg996r/firmware/bridge.py --leader /dev/cu.LEADER
# Optional only after calibration, supported follower at home, and power safety checks:
python so101-mg996r/firmware/bridge.py --leader /dev/cu.LEADER --follower /dev/cu.FOLLOWER --arm
```

Bridge is monitor-only without a follower/`--arm`. It requires STOP acknowledgement,
fresh valid encoder data and home before requesting ARM. Firmware applies slow
slew, range/pulse checks and a 250 ms command watchdog. `STOP` disables PWM.
The bridge's table check is conservative bounding-box testing; **it is not a
self-collision/path planner**. The website is offline and never controls motors.

## Verification and limits

All twelve unique printed meshes are closed, positive-volume single shells.
Exported meshes are hash-checked before publication. Six cartridge insertions,
tab lands/shanks and rotor screw-land checks pass. Full cartridge rotation at
5° increments has zero positive overlap; 36 assembled-PCB slide samples clear.
72 full-arm poses: **70 internally clear; two folded poses collide**. Eleven
intersect the table. Both failures remain in the report, not hidden. Viewer
guards detect those samples, table contact and preserve clear home/small motions.
This is sampled CAD testing, not continuous swept-path certification. It does
not validate printed tolerances, strength, screw threads, cables, torque, sensor
noise, thermal performance or payload. Test one cartridge and unpowered assembly
before spending material on the entire robot.

## Sources / attribution

- [TheRobotStudio SO-ARM100 / SO101](https://github.com/TheRobotStudio/SO-ARM100): original geometry, Apache-2.0; preserved in `source/` with hashes.
- [Adafruit AS5600 PCB](https://github.com/adafruit/Adafruit-AS5600-Magnetic-Angle-Sensor-PCB), commit `e146e77404551f1ae0619f6627bcc4435d81b0eb`: board outline and hole centres from Eagle. Adafruit Industries, CC BY-SA; licence/attribution shipped with kit.
- [Adafruit pinouts](https://learn.adafruit.com/adafruit-as5600-magnetic-angle-sensor/pinouts): 3.3 V wiring and fixed address.
- [AS5600 datasheet](https://cdn-learn.adafruit.com/assets/assets/000/138/130/original/Magnetic_Rotary_Position_Sensor_AS5600_Datasheet.pdf?1751470027=): 12-bit angle, magnetic status and magnet requirements.
- [TI TCA9548A](https://www.ti.com/product/TCA9548A): isolated selectable I²C channels.

The PCB drawing is not relicensed under the robot's licence. Keep upstream
attributions with redistributed source/derived reference geometry.
