# One-ESP32 wiring: encoder leader → Pi 4B → MG996R follower

This is the **one-ESP32 alternative** requested for the Thenar arms. The ESP32 reads the six leader encoders; the Raspberry Pi 4B receives their data over USB and connects to the follower's PCA9685 PWM board over I²C. The PCA9685, **not six Pi GPIO pins**, generates the servo pulse channels.

```text
6 × AS5600 ── TCA9548A CH0–5 ── ESP32 (leader) ── USB data ── Pi 4B
                                                                 │ I²C-1
                                                                 ▼
                          6 × MG996R ◀── PCA9685 CH0–5 ◀── Pi GPIO header
                                  ▲              ▲
                                  └──── separate regulated 6 V, fuse/switch
```

This wiring has **not been physically tested** with the purchased boards. The current `firmware/bridge.py` speaks to a *second ESP32* on the follower; it does **not yet implement Pi-direct PCA9685 control**. Wiring this arrangement alone will not make the arm move. Keep the servo supply switched off until a Pi-side driver, calibration, and safety checks are ready.

## Connections, with power OFF

| From | To | Purpose |
| --- | --- | --- |
| ESP32 3V3 and GND | TCA9548A logic supply and GND; sensor 3V3 and GND | 3.3 V sensor bus; never servo power |
| ESP32 GPIO21 / GPIO22 | TCA9548A upstream SDA / SCL | Leader I²C |
| TCA9548A channels 0–5 SDA/SCL | One AS5600 SDA/SCL per channel | Six identical-address sensors (0x36) |
| ESP32 USB | Pi 4B USB-A port, **data-capable** cable | Leader serial data |
| Pi physical pin **1** (3V3) | PCA9685 **VCC** | Logic power only |
| Pi physical pin **6** (GND) | PCA9685 **GND** | Common logic/servo reference |
| Pi physical pin **3** (GPIO2 / SDA1) | PCA9685 **SDA** | I²C-1 data |
| Pi physical pin **5** (GPIO3 / SCL1) | PCA9685 **SCL** | I²C-1 clock |
| Pi physical pin **11** (GPIO17) | PCA9685 **OE**, if exposed | HIGH disables PWM; this is **not** an emergency stop |
| PCA9685 servo outputs 0–5 | MG996R signal leads, one per joint | Positional pulse signal |
| Separate regulated **6 V +** through fuse and accessible cut-off | PCA9685 **V+** / rated servo power distribution | Servo power, **not** Pi 5 V |
| Separate 6 V supply − | PCA9685 servo GND / common GND | Return path; shared with Pi logic GND |
| Pi 4B USB-C | Its own suitable 5 V / 3 A power supply | Pi power only |

On typical servo plugs, brown/black is ground, red is V+, and orange/yellow is signal, **but verify the markings and wiring of the servos you own**. The exact PCA9685 pin order, OE availability/default state, and power-terminal current rating vary by breakout. Follow the actual board silkscreen and seller documentation rather than the illustration in the video. Six MG996R motors can draw substantial peak current; select the 6 V supply, fuse, wire gauge, connectors, and distribution board from measured current and the purchased hardware ratings. Do not assume the PCA9685 board's copper traces can distribute any arbitrary current.

The PCA9685 **VCC** is 3.3 V logic; **V+** is the separate servo supply. Their grounds must share a reference, but their positive rails must **never** be tied together. Use a physical cut-off in the 6 V rail. OE can default to enabled on some boards, and software can crash or retain the last commanded pulse. Keep servo power off during boot and setup; confirm OE behavior on your actual board before relying on it.

## Bring-up order

1. With the 6 V servo rail **off**, verify every wire against the table and check for shorts/polarity errors.
2. Power the Pi from USB-C and the leader ESP32 from Pi USB. Run the existing leader-only monitor mode; confirm six stable encoder readings.
3. Enable Pi I²C-1 and confirm that the PCA9685 responds at its expected address (usually `0x40`) before any servo is plugged in.
4. Implement and bench-test a Pi-side PCA9685 follower driver with a disabled-by-default output, stale-leader timeout, home-pose check, per-joint calibrated pulse limits, and a manual disarm path. The current two-ESP32 bridge cannot do this step.
5. Support the follower and connect **one unloaded servo**. Establish its safe centre, direction, mechanical limits, and supply behavior before trying the remaining five.

Sources: [Raspberry Pi 4B GPIO and power documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html), [Adafruit PCA9685 pin/power explanation](https://learn.adafruit.com/16-channel-pwm-servo-driver?view=all), [Adafruit Pi-to-PCA9685 wiring example](https://learn.adafruit.com/adafruit-16-channel-servo-driver-with-raspberry-pi/hooking-it-up). This is a nominal wiring plan, not a certification or physical validation report.
