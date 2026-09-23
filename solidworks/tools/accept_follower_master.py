import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2]
for script,args in [('finish_native_limit_configurations.py' if '--resume' in sys.argv else 'create_native_limit_mates.py',['follower']),('validate_real_limits.py',['follower']),('audit_native_mate_connections.py',['follower']),('verify_master_assembly.py',['follower']),('capture_follower_regression_views.py',[]),('close_saved_task_documents.py',[])]:
 print('ACCEPTANCE_STAGE',script,flush=True)
 subprocess.run([sys.executable,str(root/'solidworks/tools'/script),*args],cwd=root,check=True)
