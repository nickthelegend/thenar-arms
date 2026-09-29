# Thenar one-ESP32 connection film

Editable HyperFrames source for the 90-second video published at
`https://nickthelegend.github.io/thenar-arms/wiring-video.html`.

The film illustrates the **one ESP32 for the encoder leader + Pi 4B directly to
PCA9685 for the follower** arrangement. It is a connector-level instructional
diagram, not real footage or evidence of a working electrical build. Read
`so101-mg996r/RASPBERRY-PI-DIRECT-FOLLOWER.md` before wiring anything; the
existing `firmware/bridge.py` still targets a second ESP32.

From this directory:

```sh
npm run check
npm run render -- --quality delivery --output renders/thenar-wiring-one-esp-90s.mp4
```

The checked 1920 × 1080, 30 fps H.264 render is 90 seconds. The site serves
it at `robot-studio/public/video/thenar-wiring-90s.mp4` to preserve the earlier
video URL while replacing the obsolete two-ESP32 content.
