# Canonical visual pose comparison

Native SolidWorks views and MuJoCo URDF visual renders use the same five joint vectors. Camera framing, material shading and scene origins differ; these are visual orientation/silhouette checks, not a pixel-equality test. All 19 component transforms are checked numerically in each captured CAD pose; the full 28-pose URDF/MuJoCo regressions are recorded separately. MuJoCo uses forward kinematics only. Inferred physical masses are rejected and no dynamics stepping is claimed.

## ZERO

Joint degrees: [0, 0, 0, 0, 0, 0]. Native CAD/source position discrepancy: 1.29614459e-09 mm.

SolidWorks:

![SolidWorks ZERO](D:/Project/so-101-mg996r/thenar-arms/verification/pose_images/solidworks_ZERO.png)

MuJoCo visual geometry:

![MuJoCo ZERO](D:/Project/so-101-mg996r/thenar-arms/verification/pose_images/mujoco_ZERO.png)

## J1_MAX

Joint degrees: [85, 0, 0, 0, 0, 0]. Native CAD/source position discrepancy: 2.31808751e-09 mm.

SolidWorks:

![SolidWorks J1_MAX](D:/Project/so-101-mg996r/thenar-arms/verification/pose_images/solidworks_J1_MAX.png)

MuJoCo visual geometry:

![MuJoCo J1_MAX](D:/Project/so-101-mg996r/thenar-arms/verification/pose_images/mujoco_J1_MAX.png)

## J2_MIN

Joint degrees: [0, -80, 0, 0, 0, 0]. Native CAD/source position discrepancy: 2.22399225e-09 mm.

SolidWorks:

![SolidWorks J2_MIN](D:/Project/so-101-mg996r/thenar-arms/verification/pose_images/solidworks_J2_MIN.png)

MuJoCo visual geometry:

![MuJoCo J2_MIN](D:/Project/so-101-mg996r/thenar-arms/verification/pose_images/mujoco_J2_MIN.png)

## MULTI

Joint degrees: [20, -30, 40, -20, 30, 25]. Native CAD/source position discrepancy: 1.30281808e-09 mm.

SolidWorks:

![SolidWorks MULTI](D:/Project/so-101-mg996r/thenar-arms/verification/pose_images/solidworks_MULTI.png)

MuJoCo visual geometry:

![MuJoCo MULTI](D:/Project/so-101-mg996r/thenar-arms/verification/pose_images/mujoco_MULTI.png)

## HOME

Joint degrees: [0, -25, 35, 0, 0, 20]. Native CAD/source position discrepancy: 1.14827369e-09 mm.

SolidWorks:

![SolidWorks HOME](D:/Project/so-101-mg996r/thenar-arms/verification/pose_images/solidworks_HOME.png)

MuJoCo visual geometry:

![MuJoCo HOME](D:/Project/so-101-mg996r/thenar-arms/verification/pose_images/mujoco_HOME.png)
