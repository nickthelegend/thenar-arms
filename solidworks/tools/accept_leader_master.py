import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
for script,args in [('validate_real_limits.py',['leader']),('audit_native_mate_connections.py',['leader']),('verify_master_assembly.py',['leader']),('close_saved_task_documents.py',[])]:
 print('ACCEPTANCE_STAGE',script,flush=True)
 subprocess.run([sys.executable,str(root/'solidworks/tools'/script),*args],cwd=root,check=True)
