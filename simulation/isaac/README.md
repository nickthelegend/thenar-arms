# Isaac Sim import handoff

Import `source_urdf/so101.urdf` using the URDF importer in the installed Isaac Sim release. Relative mesh paths are self-contained. Follow `config/import_requirements.yaml`; compare the same joint vectors to `validation/canonical_pose_reference.json` in metres before accepting articulation.

Isaac Sim was unavailable in this task environment, so no import, USD or dynamics validation is claimed. `usd/` is intentionally empty. Missing physical inertials and unaccepted convex collision proxies block trustworthy physics. Do not accept automatic density, mass, drive gains or single-convex-hull approximations as measured robot data. Preserve the original dimensions and source joint limits.
