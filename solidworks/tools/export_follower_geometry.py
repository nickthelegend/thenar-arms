from export_part_mesh import main,ROOT
import json
out=ROOT/'solidworks/exports/visual_mm';out.mkdir(parents=True,exist_ok=True)
for row in json.loads((ROOT/'solidworks/evidence/all_part_body_checks.json').read_text()):
    from pathlib import Path
    main(Path(row['path']),out/(row['part']+'.stl'))
