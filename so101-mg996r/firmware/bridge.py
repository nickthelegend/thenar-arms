"""USB encoder monitor / opt-in follower bridge. Never arms by default.

python bridge.py --leader /dev/cu.LEADER
python bridge.py --leader /dev/cu.LEADER --follower /dev/cu.FOLLOWER --arm
"""
import argparse,json,math,time,itertools
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
LO=np.array([-85,-80,-80,-80,-85,0]);HI=np.array([85,80,80,80,85,70])
HOME=np.array([0,-25,35,0,0,20])

def rotation(values):
    x,y,z=np.radians(values);a,b,c=np.cos([x,y,z]);u,v,w=np.sin([x,y,z])
    return np.array([[1,0,0],[0,a,-u],[0,u,a]])@np.array([[b,0,v],[0,1,0],[-v,0,b]])@np.array([[c,-w,0],[w,c,0],[0,0,1]])

class TableGuard:
    """Conservative transformed bounding boxes, not a full collision solver."""
    def __init__(self):
        folder=ROOT/'output/follower-r3'
        self.m=json.loads((folder/'assembly-source.json').read_text())
        self.bounds={p['id']:np.asarray(p['bounds_mm']) for p in self.m['conversion_units']}
    def safe(self,q):
        ws={}
        for n in self.m['nodes']:
            t=np.eye(4);t[:3,:3]=rotation(n['rotation']);t[:3,3]=n['position']
            if n['joint'] is not None:t[:3,:3]=t[:3,:3]@rotation([0,0,q[n['joint']]])
            ws[n['id']]=(ws[n['parent']] if n['parent'] else np.eye(4))@t
        for i in self.m['instances']:
            if i['robot']!='follower':continue
            bb=self.bounds.get(i['part'],np.array([[-24.95,-10,-28.5],[29.05,10,16.7]]))
            t=np.eye(4);t[:3,:3]=rotation(i['rotation']);t[:3,3]=i['position'];t=ws[i['node']]@t
            lowest=t[2,3]+np.minimum(t[2,:3]*bb[0],t[2,:3]*bb[1]).sum()
            if lowest<-.2:return False
        return True

def parse(line):
    p=line.split()
    if len(p)!=7 or p[0]!='L':return None
    try:q=np.array([float(x) for x in p[1:]])
    except ValueError:return None
    return q if np.isfinite(q).all() and np.all(q>=LO) and np.all(q<=HI) else None

def main():
    import serial
    ap=argparse.ArgumentParser();ap.add_argument('--leader',required=True);ap.add_argument('--follower');ap.add_argument('--arm',action='store_true');a=ap.parse_args()
    if a.arm and not a.follower:ap.error('--arm requires --follower')
    leader=serial.Serial(a.leader,115200,timeout=.02,write_timeout=.1)
    follower=serial.Serial(a.follower,115200,timeout=.02,write_timeout=.1) if a.follower else None
    guard=TableGuard();last=None;armed=False;requested=False
    try:
        time.sleep(2);leader.reset_input_buffer()
        if follower:
            follower.reset_input_buffer();follower.write(b'STOP\n')
            deadline=time.monotonic()+2
            while time.monotonic()<deadline:
                if follower.readline(256).decode(errors='replace').strip().startswith('STOP'):break
            else:raise RuntimeError('Follower did not acknowledge STOP; refusing to arm')
            leader.reset_input_buffer()
        while True:
            if leader.in_waiting>512:raise RuntimeError('Encoder backlog: stale frames discarded; reconnect to resume')
            line=leader.readline(256).decode(errors='replace').strip();q=parse(line)
            if line:print(line,flush=True)
            if follower and line.startswith('FAULT'):raise RuntimeError(line)
            if q is not None:
                last=time.monotonic()
                if follower:
                    if not guard.safe(q):raise RuntimeError('Follower would enter the tabletop')
                    follower.write(('Q '+' '.join(f'{v:.3f}' for v in q)+'\n').encode())
                    if a.arm and not requested:
                        if np.max(abs(q-HOME))>3:raise RuntimeError('Place leader and supported follower at displayed home before arming')
                        follower.write(b'ARM\n');requested=True
            if follower:
                reply=follower.readline(256).decode(errors='replace').strip()
                if reply:print('FOLLOWER',reply,flush=True)
                if reply=='ARMED':armed=True
                elif requested and reply.startswith('STOP'):raise RuntimeError(reply)
                if last is not None and time.monotonic()-last>.25:raise RuntimeError('Encoder stream timeout')
    finally:
        if follower:
            try:follower.write(b'STOP\n')
            finally:follower.close()
        leader.close()

if __name__=='__main__':main()
