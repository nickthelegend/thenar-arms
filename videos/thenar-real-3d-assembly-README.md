# Thenar real 3D assembly film

[Watch the 180-second MP4](../robot-studio/public/video/thenar-real-3d-assembly-180s.mp4) · 1920 × 1080 · 25 fps

This replaces the earlier static-card assembly guide. It loads the 27 actual project STL meshes through the same Three.js assembly manifest as the robot viewer and animates 92 mesh instances through 80 physical assembly steps into their recorded CAD transforms. It shows the passive leader L1 first, joint by joint, then the MG996R follower R3, servo by servo, and finishes with both complete assemblies.

The video renders printed links, six encoder cartridges, six AS5600 board assemblies, twelve 688ZZ bearings, six rotors, six magnet cups/magnets, six MG996R body reference meshes, and six metal horn reference meshes. Hardware without an STL in the manifest—individual screws, nuts, washers, cables, power supply, and boards outside the arm—is called out in labels but **not falsely modeled or placed**. [Raspberry Pi 4B wiring](../so101-mg996r/RASPBERRY-PI-4B.md) is documented separately.

The 3D placements are nominal CAD targets, **not proof of physical fit, strength, collision-free travel or successful electronics operation**. Dry-fit your actual purchased servos/horns and first cartridge, verify bearing/magnet readings, and test all joint motions unpowered before applying servo power.

To watch the real-time 3D animation in the project website, start `robot-studio` with `npm run dev` and open `/assembly-video.html`. The MP4 was captured directly from that Three.js scene, not made from static slides.
