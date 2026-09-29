---
mode: autonomous
message: "One ESP32 reads the leader; the Pi 4B controls the follower PCA9685 directly over I²C."
audience: Thenar arm builder
duration: 90
---

## Frame 1

- status: animated
- src: index.html
- shape: one continuous connector-level wiring-bench illustration, no hard cuts
- motion: `svg-path-draw` for each physical wire; component opacity reveals; spring entrance for the final guarded-test cue
- beat: 0–8 s — one ESP32 only; Pi is host and PWM controller, not a servo supply
- beat: 8–25 s — six AS5600 sensors to TCA9548A channels 0–5; 3.3 V/GND and I²C
- beat: 25–38 s — mux to leader ESP32 GPIO21/22, then USB to Pi
- beat: 38–56 s — Pi physical pins 1/3/5/6/11 to PCA9685 VCC/SDA/SCL/GND/OE
- beat: 56–72 s — PCA9685 channels 0–5 to MG996R signals; separate fused 6 V rail and common GND
- beat: 72–90 s — power-off checks, leader-only monitor, new Pi direct-driver software requirement, servo calibration, guarded arming
- why: turn the missing electronics into a traceable, buildable connection order without overstating validation
