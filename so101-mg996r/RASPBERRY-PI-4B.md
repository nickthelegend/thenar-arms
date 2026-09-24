# Raspberry Pi 4B host for the Thenar leader + follower

The Pi 4B runs `firmware/bridge.py`; it **does not drive the six MG996R servos directly**. Use one USB-connected ESP32 for the passive encoder leader and a second USB-connected ESP32 for the powered follower.

```text
6 × AS5600 → TCA9548A channels 0–5 → leader ESP32 ── USB 1 ──┐
                                                            Raspberry Pi 4B
6 × MG996R ← PCA9685 channels 0–5 ← follower ESP32 ─ USB 2 ──┘
      ↑               ↑
      └── separate regulated 6 V servo supply; common GND ──────┘
```

## Wiring essentials

| Item | Connect |
| --- | --- |
| Pi 4B power | Its own 5 V / 3 A USB-C supply, per [Raspberry Pi's guidance](https://www.raspberrypi.com/documentation/computers/getting-started.html) |
| Leader ESP32 | Pi USB port; ESP32 GPIO21 SDA and GPIO22 SCL to TCA9548A upstream; 3.3 V logic; AS5600 sensors each on separate mux channels 0–5 |
| Follower ESP32 | Second Pi USB port; GPIO21 SDA and GPIO22 SCL to PCA9685; GPIO25 to PCA9685 OE, with a 10 kΩ pull-up from OE to 3.3 V |
| Servo signal | PCA9685 channels 0–5 to the six MG996R signal leads |
| Servo power | Separate regulated 6 V supply to PCA9685 servo V+ and GND; **not** Pi 5 V, USB, or ESP32 3.3 V |
| Ground | Tie follower servo-supply GND to PCA9685 and follower ESP32 GND; verify polarity before power |

The 6 V / 10–15 A range in [R3-PRINT.md](R3-PRINT.md) is a planning range, **not** a measured current specification for your purchased servos. Size the supply and wiring after measuring loaded/stall current, and add a means of disconnecting servo power. [Adafruit's PCA9685 guidance](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all) also separates logic power and external servo power.

## Run on Raspberry Pi OS

The Pi needs Raspberry Pi OS, Python 3, two USB data cables, `numpy`, and `pyserial`. From the repository directory on the Pi:

```bash
python3 -m venv --system-site-packages .venv
.venv/bin/pip install numpy pyserial
ls -l /dev/serial/by-id/
```

Use the two stable `/dev/serial/by-id/...` device names shown by that last command, if available. They must point to *different* ESP32 boards. If the directory is empty, inspect `ls /dev/ttyUSB* /dev/ttyACM*` after connecting each board one at a time. For a Linux serial permission error, add your user to the `dialout` group and log in again.

Start with **leader-only monitor mode**, which sends no follower motion:

```bash
.venv/bin/python so101-mg996r/firmware/bridge.py --leader /dev/serial/by-id/YOUR_LEADER_ID
```

The leader firmware should emit six angles in lines beginning `L`. Only after dry-fitting the printed links, confirming magnet readings, centering all six servos, testing power/GND, calibrating horn orientation and physical travel, and supporting the follower at home should you connect the follower and opt into arming:

```bash
.venv/bin/python so101-mg996r/firmware/bridge.py --leader /dev/serial/by-id/YOUR_LEADER_ID --follower /dev/serial/by-id/YOUR_FOLLOWER_ID --arm
```

The bridge opens both serial links at 115200 baud and attempts a STOP handshake before arming. Its software angle limits and tabletop guard are not a substitute for measured hard-stop limits, current protection, or an accessible power cutoff. The MG996R model is a **180° positional servo**, so do not command motion beyond its calibrated physical range. The repository's leader/follower firmware source still needs to be flashed to the respective ESP32s; this guide does not claim that electronics or the printed mechanism have been physically validated.
