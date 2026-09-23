"""Task-local MCP bridge to the installed SolidWorks COM API.

No listener, startup registration, or external service. Launched on demand over stdio.
"""
# Load native numerical DLLs before starting the async stdio worker threads.
import numpy
import build_follower_assembly
import build_leader_assembly
from mcp.server.fastmcp import FastMCP
from sw_api import attach,model
import contextlib,io,json
mcp=FastMCP('SO101 SolidWorks reconstruction')
@mcp.tool()
def solidworks_status()->dict:
    """Read the attached SolidWorks session without opening or closing documents."""
    s=attach();d=model(s.ActiveDoc)
    return {'revision':s.RevisionNumber(),'document':d.GetTitle(),'path':d.GetPathName()}
@mcp.tool()
def build_nominal_hardware(component:str)->dict:
    """Create editable source-dimension hardware: component is MG996R or horn."""
    from native_hardware import make
    return make(component)
@mcp.tool()
def import_follower_reference(part:str)->dict:
    """Preserve an existing R3 printing unit as a labelled solid-body reference checkpoint."""
    allowed=['Base','Shoulder','Upper_arm','Forearm','Wrist_pitch_roll','Gripper_body','Moving_jaw']
    if part not in allowed:raise ValueError('Unknown source printing unit')
    from import_reference import run,ROOT
    with contextlib.redirect_stdout(io.StringIO()):run(part+'_MG996R_R3')
    return json.loads((ROOT/'solidworks/evidence'/(part+'_MG996R_R3_import.json')).read_text())
@mcp.tool()
def preserve_all_follower_parts()->dict:
    """Create missing labelled reference checkpoints for the seven source printing units."""
    from import_reference import ROOT
    rows=[]
    for part in ['Base','Shoulder','Upper_arm','Forearm','Wrist_pitch_roll','Gripper_body','Moving_jaw']:
        evidence=ROOT/'solidworks/evidence'/(part+'_MG996R_R3_import.json')
        row=json.loads(evidence.read_text()) if evidence.exists() else import_follower_reference(part)
        rows.append({'part':part,'body_count':row['body_count'],'save_error':row['save_error']})
    return {'parts':rows,'native_parametric_reconstruction':False}
@mcp.tool()
def rebuild_hardware_library()->dict:
    """Rebuild servo and metal horn from source dimensions with sketch inference disabled."""
    from native_hardware import make
    return {'parts':[{'path':r['path'],'body_count':r['body_count'],'save_error':r['save_error']} for r in [make('MG996R'),make('horn')]]}
@mcp.tool()
def build_follower_work_in_progress_assembly()->dict:
    """Build the source-layout follower WIP and add physical mates; unresolved surface part stays labelled."""
    from build_follower_assembly import main,ROOT
    with contextlib.redirect_stdout(io.StringIO()):main()
    return json.loads((ROOT/'solidworks/evidence/follower_assembly_build.json').read_text())
@mcp.tool()
def add_follower_pose_controller()->dict:
    """Add named, source-derived native mate-controller positions to the tested follower WIP."""
    from add_pose_controller import main,ROOT
    with contextlib.redirect_stdout(io.StringIO()):main()
    return json.loads((ROOT/'solidworks/evidence/mate_controller.json').read_text())
@mcp.tool()
def build_passive_leader_assembly()->dict:
    """Assemble accepted L1 parts with 66 rigid locks and six hinge chains; final native limit setup is a separate acceptance stage."""
    from build_leader_assembly import main,EVIDENCE
    with contextlib.redirect_stdout(io.StringIO()):main()
    return json.loads(EVIDENCE.read_text())
@mcp.tool()
def set_robot_joint_pose(robot:str,degrees:list[float],save:bool=False)->dict:
    """Set six logical joint angles through native mates, preserving source range limits.

    robot is follower or leader. Source bounds are not physical clearance certification.
    """
    from real_limit_mates import connect_robot,set_pose,measure,mate_features
    if robot not in ['follower','leader'] or len(degrees)!=6:raise ValueError('Supply follower/leader and exactly six degree values')
    s,d,a,m,build,path=connect_robot(robot)
    if 'FREE_MOTION' not in d.GetConfigurationNames():raise RuntimeError('Master configuration setup is incomplete')
    d.ShowConfiguration2('FREE_MOTION')
    if any(not numpy.isfinite(q) or not lo<=q<=hi for q,(lo,hi) in zip(degrees,m['limits'])):raise ValueError('Angle exceeds source software bounds')
    with contextlib.redirect_stdout(io.StringIO()):
        set_pose(d,mate_features(d),degrees,m['limits'],force=True);result=measure(d,a,m,build,'MCP_REQUESTED',degrees)
    if not result['kinematic_pass']:raise RuntimeError('Native pose verification failed; changes were not saved')
    if save and d.SaveAs3(str(path),0,1)!=0:raise RuntimeError('SolidWorks save failed')
    return {k:v for k,v in result.items() if k not in ['components','joints']}
if __name__=='__main__':mcp.run(transport='stdio')
