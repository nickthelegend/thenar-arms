# Thenar Arms

An original-derived SO-101 project with two separate builds: a six-MG996R
positional-servo **follower** and a passive, six-AS5600 **encoder leader**. The
repository includes converted STL parts, Bambu P1S geometry layouts, articulated
SolidWorks assemblies, a browser-based 3D viewer, an assembly animation, and
prototype ESP32 firmware.

> **Prototype status:** CAD and software checks are documented, but the complete
> printed mechanism, purchased hardware, wiring, and powered motion have **not**
> been physically validated. There is no payload rating or print-ready G-code.

![MG996R follower and encoder leader CAD assemblies](docs/images/assembly.png)

## Start here

| What you want | Link |
|---|---|
| Inspect both arms in 3D | [Open Robot Studio](https://nickthelegend.github.io/thenar-arms/) |
| See where each part goes | [Interactive 3D assembly film](https://nickthelegend.github.io/thenar-arms/assembly-video.html) — drag the timeline or pause at a step |
| Watch offline | [180-second MP4](robot-studio/public/video/thenar-real-3d-assembly-180s.mp4) |
| Build the MG996R follower | [Follower BOM, print notes and assembly](so101-mg996r/R3-PRINT.md) |
| Build the encoder leader | [Leader BOM, print notes, wiring and calibration](so101-mg996r/ENCODER-LEADER.md) |
| Use a Raspberry Pi 4B as host | [Pi 4B wiring and bridge guide](so101-mg996r/RASPBERRY-PI-4B.md) |

The animation uses project STL meshes and nominal CAD positions. Individual
fasteners and unspecified controller boards are not modeled. It is an assembly
guide, **not** proof that parts fit, move safely, or work electrically.

## Choose a build

| | MG996R follower R3 | Passive encoder leader L1 |
|---|---|---|
| Actuation / sensing | Six 180° positional MG996R servos; no external follower encoders | Six passive AS5600 angle-sensing joints; no drive servos |
| Print set | 7 joined units, 2 P1S geometry-only layouts | 37 pieces from 12 unique STLs, 3 P1S geometry-only layouts |
| Essential hardware | 6 matching 25T metal-disc horns, ESP32, PCA9685, separate regulated 6 V servo supply, mounting fasteners | 6 Adafruit 6357 AS5600 boards, 12 **688ZZ 8 × 16 × 5 mm** bearings, 6 diametric Ø6 × 2 mm magnets, ESP32, TCA9548A, fasteners |
| Files | [Follower STL/3MF ZIP](so101-mg996r/output/follower-r3/SO101-MG996R-R3-PROTOTYPE.zip) | [Leader STL/3MF/firmware ZIP](so101-mg996r/output/encoder-leader-l1/SO101-AS5600-LEADER-L1.zip) |
| Detailed guide | [R3-PRINT.md](so101-mg996r/R3-PRINT.md) | [ENCODER-LEADER.md](so101-mg996r/ENCODER-LEADER.md) |

These are **converted parts**, not the stock SO-101 Ender plates. Do not mix R3
follower brackets, L1 leader parts, earlier revisions, and untouched stock
parts. The original link shapes and source datums are retained; this is not a
whole-arm scale-up. Case, horn, bearing and board dimensions are nominal design
inputs, not measurements of the user's purchased components.

**Before a full print:** inspect every sliced layer in Bambu Studio, then
print and dry-fit one mount or one five-piece encoder cartridge. The 3MF files
are layouts, **not approved sliced projects**. The follower and leader guides
document unresolved slicer clipping/layer-review findings. PETG is the planned
structural material; a successful PLA test does not establish strength.

![P1S geometry layouts for the converted parts](docs/images/print-plates.png)

## CAD, simulation and evidence

The [SolidWorks reconstruction release](https://github.com/nickthelegend/thenar-arms/releases/tag/solidworks-r3-l1-2026-09-23)
contains separate articulated follower and leader assemblies. Open the
[follower master](solidworks/assemblies/SO101_Follower_Master.SLDASM) or
[leader master](solidworks/assemblies/SO101_Leader_Master.SLDASM) with their
`solidworks/parts/` and `solidworks/hardware/` folders alongside them. See the
[SolidWorks guide](solidworks/README.md) and [reconstruction report](docs/final_report.md).

| Native assembly | Components | Moving joints | Recorded SolidWorks pose checks |
|---|---:|---:|---:|
| Follower R3 | 19 | 6, including jaw | 28/28 passed |
| Leader L1 | 73 | 6, including trigger | 28/28 passed |

The SolidWorks work did **not** modify the 330 existing project STL/3MF files;
those files do not need reprinting because of that reconstruction. Its CAD
solids are not byte-identical to the STLs. The reports document sampled surface
differences, a small leader-forearm solid-body separation, and collision
results. ROS 2 description and MuJoCo kinematics passed recorded pose checks;
ROS 2 visualization, Isaac import and physical dynamics were not tested.

![Exploded encoder cartridge CAD](docs/images/encoder-exploded.png)

### Validation boundaries

| Check | Recorded result |
|---|---|
| Closed single-shell print meshes | 7 follower + 12 unique leader meshes |
| Nominal mounting interfaces | 6/6 follower and 6/6 leader checks passed |
| Sampled internal collision poses | Follower 72/72 clear; leader 70/72 clear. Two folded leader collisions and table intersections remain documented. |
| Encoder cartridge | Sampled rotation/PCB checks show no positive overlap; magnet gap is nominally 2 mm. |
| P1S layouts | Five geometry layouts fit the P1S envelope with 12 mm part spacing. Slicing release is **not cleared**. |
| Firmware | Both ESP32 roles compile and host motion-math tests pass; follower stays locked until calibration. |
| Real hardware | **Not validated:** actual fits, bearings, sensors, wiring, strength, powered travel or payload. |

The browser preview checks discrete poses; it is not a swept-path or physical
safety certificate. The firmware STOP/OE path does not cut servo power. Clamp
and support the arm, and provide an accessible hardware power disconnect.
See the [encoder verification report](so101-mg996r/output/encoder-leader-l1/verification.json)
for machine-readable results.

## Run Robot Studio locally

```sh
cd robot-studio
npm ci
npm run dev
```

Open `http://127.0.0.1:5173/` for the arm viewer,
`http://127.0.0.1:5173/assembly-video.html` for the seekable 3D assembly
animation, or `http://127.0.0.1:5173/?geometry=clearance&view=fit-test` for
print-layout geometry. `?geometry=original` shows untouched upstream references.
The website does not connect to hardware.

<details>
<summary>Reproduce the current CAD and validation checks</summary>

Use a Python 3.12 environment with
[`so101-mg996r/requirements-cad.txt`](so101-mg996r/requirements-cad.txt)
installed, then run from the repository root:

```sh
python so101-mg996r/tools/build_encoder_leader.py
python so101-mg996r/tools/verify_encoder_leader.py
python so101-mg996r/tools/pack_encoder_leader.py
cd robot-studio
node scripts/verify-preview.mjs
node scripts/verify-r3.mjs
node scripts/verify-encoder.mjs
npm run build
```

Optional publishing/slicing scripts and firmware commands are in the kit
guides. No command here automatically flashes firmware or arms servos.

</details>

## Source and licences

The original SO-101 design is from
[TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100),
Apache-2.0; its licence is preserved at `so101-mg996r/source/LICENSE`.
The AS5600 board drawing is from
[Adafruit Industries](https://github.com/adafruit/Adafruit-AS5600-Magnetic-Angle-Sensor-PCB),
CC BY-SA, with attribution in `so101-mg996r/source/encoder/`.
Third-party assets keep their respective licences; this repository does not
relicense them. The images above are CAD renders, not photos of a tested robot.
