# MG996R follower and encoder leader — staged BOM

## Current R3 follower BOM

Use the **[R3-PRINT.md prototype BOM](R3-PRINT.md#prototype-bom)** for the seven
converted arm units. It specifies six MG996Rs (four owned, two additional), six
metal disc horns, 24 M3 × 12 tab screws, 24 nuts, 48 washers, 24 M3 × 8 horn
screws, six matching horn-retaining screws, controller/power planning and clamps.
Two geometry-only P1S layouts are included; sliced downloads are withheld pending
toolpath review. This remains an unpowered, nominal-fit assembly prototype.

The R1 list below is preserved as **historical background**, not the R3 assembly
or fastener schedule. The encoder leader and electronics enclosure remain open.

## Historical R1 bench-fit BOM

Revision: 2026-09-17, bench-fit prototype R1. **Not a final full-arm procurement
release.** Your purchased MG996Rs have user-confirmed 180° travel; their dimensions,
horns and usable powered endpoints are not measured yet.

## Print/test now: one unpowered servo

| Item | Quantity | Specification / purpose |
|---|---:|---|
| Your purchased MG996R | 1 from the existing 4 | Leave disconnected; remove its horn for insertion |
| Body/tab gauge | 1 print | 41.5 × 20.6 mm opening; nominal 49.5 × 10 mm hole centres |
| Original-derived wrist holder | 1 print, after gauge fit | 4 mm tab ledges, 5 × 3.4 mm slots; bench only |
| Horn-pattern gauge | 1 optional print | Checks proposed 14 mm PCD, four-hole disc; not spline fit |
| M3 × 12 mm machine screws | 4 | Only if actual tab holes accept M3 without drilling |
| M3 hex nuts | 4 | Nominal 5.5 mm across flats; access bores are 6.8 mm |
| M3 flat washers | 8 | One under each head and nut; approximately 7 mm outside diameter |
| PETG | About 5 g gauges / 24 g full test plate | Slicer estimates including supports/brim; extra for purge |
| Calipers, ruler, small driver and nut tool | 1 set | Record actual dimensions; do not force mismatched hardware |

The M3 × 12 stack assumes a 4 mm ledge, 2.6 mm tab, about 1 mm combined washer
thickness and a 2.4 mm nut. Confirm actual stack before tightening; screw tips must
not touch the servo. No full-arm screws, bearing axles or spline interfaces are
implicitly approved by this test.

## Planned follower: six controlled axes

| Component | Total needed | Already owned / purchase status |
|---|---:|---|
| Matching positional MG996R servos | 6 | 4 reported owned; 2 more after fit/travel checks |
| Metal servo horns with matching spline | 6 | Supplied horns unmeasured. Proposed option: 25T, Ø20 mm disc, four M3 holes on Ø14 mm PCD; verify on your shaft first |
| Correct central horn-retaining screws | 6 | Use screws supplied for the exact shaft; do not assume M3 |
| ESP32 development board | 1 | Proposed controller; matching USB cable ×1 |
| PCA9685 PWM breakout | 1 | Six channels used; 3.3 V logic; replaces stock STS bus-controller function |
| Regulated external servo power supply | 1 | 6 V, 10–15 A planning range; final sizing from measured units, load and wiring |
| Servo power distribution / protected harness | 1 | Rated for chosen current, individual power branches, common ground; no unverified breakout terminal or breadboard for total current |
| DC-rated power cutoff, fuse holder and fuse | 1 each | Ratings selected with final supply, conductors and connectors; cutoff interrupts servo power |
| Servo extension leads | Up to 6 | Lengths after actual routing, slack at travel limits |
| I²C / signal wiring and connectors | 1 set | ESP32 to PCA9685, secure connections and strain relief |
| Servo-tab screws / nuts / washers | Up to 24 / 24 / 48 | Intended four-per-servo pattern; NOT a released full-arm fastener schedule |
| Horn-to-link screws | TBD | Length from final engagement; tips must not touch servo case |
| Opposite-side bearings, shafts, spacers, retainers | TBD | Essential load-path redesign; do not order guessed sizes |
| Link/base fasteners, inserts and desk clamps | TBD | Counts/lengths follow final interfaces; stock STS kit is not automatically transferable |
| Printed arm parts | Pending | Original 11 follower parts are sources, not MG996R-ready prints |

No external encoders are required on the follower under your requested approach.
MG996Rs have internal position control, but the ordinary 3-wire interface does not
return measured joint position. An animation cannot prove a physical joint followed
its command.

The stock WaveShare STS serial-bus controller is not the PWM driver for this
conversion. Its stock mounting plate does not establish ESP32/PCA9685 fit.
Electronics mounting and the final harness remain to be designed.

### Power and operating limits

TowerPro publishes 4.8–6.6 V and 1.4 A stall current for its own MG996R. Six such
units total 8.4 A at that stated stall current, before headroom; your generic units
may differ. The supply range above is a planning estimate, not a tested rating.
Never deliberately stall all joints to size the supply. Do not power servos from
USB, the ESP32 3.3 V pin, or its regulator.

PCA9685 VCC uses controller logic voltage; servo power is separate, with common
ground. Software output-disable does not replace a physical power cutoff.
Support the arm before cutting power because joints can drop. No payload, speed,
continuous torque or thermal rating is established. Test one unloaded servo first,
then a mechanically approved and supported joint.

Sources: [TowerPro specification](https://towerpro.com.tw/product/mg996r/),
[Adafruit driver power/pinouts](https://learn.adafruit.com/16-channel-pwm-servo-driver/pinouts),
[proposed metal horn](https://www.handsontec.com/dataspecs/accessory/25T%20Servo%20Disc.pdf).
These reference specifications do not prove the Amazon unit's dimensions.

## Later: passive encoder leader, not mechanically converted yet

| Component | Planned quantity | Status |
|---|---:|---|
| AS5600 angle-sensor breakout | 6 | Five arm axes plus trigger; select exact board outline/hole pitch |
| Diametrically magnetized on-axis magnets | 6 | Match sensor field/gap requirements; not axially magnetized discs |
| TCA9548A I²C multiplexer breakout | 1 | Separates identical-address sensor channels |
| Leader ESP32 and USB cable | 1 each, optional | For a separate controller; short shared-controller bench setup can use follower ESP32 |
| Passive bearings/bushings, axles and spacers | TBD | Servo bodies cannot be removed without replacing their support function |
| Trigger spring, magnet and sensor carriers | TBD | Geometry and spring force not released |
| Leader wiring and strain relief | 1 set | Lengths after routing |

The planned leader uses **no MG996R motors**. Encoder cartridges and bearings are
not present in the displayed stock leader. Evaluate one sensor/magnet pair first,
not six mechanically unverified modules.

Sources: [AS5600 datasheet](https://look.ams-osram.com/m/7059eac7531a86fd/original/AS5600-DS000365.pdf),
[magnetic setup](https://look.ams-osram.com/m/4f8342513a447495/original/AS5600_UG000254_2-00.pdf),
[TI TCA9548A](https://www.ti.com/product/TCA9548A).

## What blocks the complete robot

The full-arm study still fails its 44 sampled poses: moving-link interferences,
wrist-servo-to-wrist-servo overlap, incomplete horn/opposite-side support interfaces,
and two open draft meshes. The standalone holder test has not been inserted into
that assembly or represented as solving the other failures. A complete verified
BOM depends on fixing those interfaces.
