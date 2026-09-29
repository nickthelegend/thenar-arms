---
workflow: general-video
flow: automation
storyboard: no
message: "Connect the passive encoder leader through one ESP32 to a Raspberry Pi 4B, then drive the MG996R follower through a Pi-connected PCA9685."
destination: website
aspect: 1920x1080
language: en
audience: Thenar arm builder
length: 90s
---

## Intent

A practical, connector-level connection walkthrough for the existing Thenar leader and follower. The user has only one ESP32 and explicitly wants it on the encoder leader; a Raspberry Pi 4B must talk to that ESP32 over one USB data cable and control the follower PCA9685 over its own I²C header. This is an animated depiction of physical connectors and leads, not footage of the user's actual boards.

## Notes

- Show six AS5600 leader encoders, TCA9548A mux, the only ESP32, Pi 4B 40-pin header, PCA9685, six MG996R servos, and separate regulated 6 V servo power.
- Show physical Pi header pin numbers: 1=3V3, 3=GPIO2/SDA, 5=GPIO3/SCL, 6=GND, 11=GPIO17/OE. Depict functional terminals, not a claim that every vendor's board has identical physical pin placement.
- Never imply Pi USB/5 V or ESP32 3V3 powers the motors. Show common ground, fuse/cutoff, 6 V switch kept off during boot, and power-off wiring order.
- End with leader-only monitor mode, then a Pi-side follower driver, physical servo calibration and one unloaded servo before any full follower arming. Current `firmware/bridge.py` still assumes a second ESP32; the one-ESP32 plan is not a completed hardware test.
- Use clear silent on-screen instructional text; no invented voice or music.
