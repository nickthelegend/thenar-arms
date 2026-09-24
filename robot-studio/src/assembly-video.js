import * as THREE from 'three';
import {STLLoader} from 'three/addons/loaders/STLLoader.js';
import {modelUrl} from './asset-path.js';

const DURATION=180, INTRO=6, LEADER_END=108, FOLLOWER_START=112, FOLLOWER_END=155;
const JOINTS=['BASE ROTATION','SHOULDER','ELBOW','WRIST PITCH','WRIST ROLL','TRIGGER'];
const $=s=>document.querySelector(s);
const stage=$('#stage'), ready=$('#ready');
function fitStage(){const scale=Math.min(innerWidth/1920,innerHeight/1080);stage.style.transform=`scale(${scale})`;stage.style.transformOrigin='top left';stage.style.left=`${(innerWidth-1920*scale)/2}px`;stage.style.top=`${(innerHeight-1080*scale)/2}px`}
fitStage();addEventListener('resize',fitStage);
const scene=new THREE.Scene();scene.background=new THREE.Color('#0b1523');scene.fog=new THREE.Fog('#0b1523',1250,2900);
const camera=new THREE.PerspectiveCamera(38,1920/1080,1,5000);camera.up.set(0,0,1);
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(1920,1080);renderer.setPixelRatio(1);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.65;stage.insertBefore(renderer.domElement,ready);
scene.add(new THREE.HemisphereLight(0xd8ebff,0x304258,2.5));
const key=new THREE.DirectionalLight(0xffffff,3);key.position.set(-400,-450,800);scene.add(key);
const rim=new THREE.DirectionalLight(0x9abfff,1.8);rim.position.set(450,300,650);scene.add(rim);
const floor=new THREE.Mesh(new THREE.PlaneGeometry(3500,3500),new THREE.MeshStandardMaterial({color:0x152539,roughness:.96}));floor.position.z=-5;scene.add(floor);
const grid=new THREE.GridHelper(2200,44,0x436079,0x263e56);grid.rotation.x=Math.PI/2;grid.position.z=-4.4;grid.material.transparent=true;grid.material.opacity=.48;scene.add(grid);
const indicator=new THREE.Mesh(new THREE.TorusGeometry(21,1.5,8,72),new THREE.MeshBasicMaterial({color:0x84fbd0,transparent:true,opacity:.8,depthTest:false}));indicator.renderOrder=8;scene.add(indicator);

const manifest=await(await fetch(modelUrl('encoder-leader-l1/manifest.json'))).json();
const geometry=new Map(),partById=new Map(manifest.parts.map(p=>[p.id,p]));
const loader=new STLLoader();
for(const p of manifest.parts){const g=await loader.loadAsync(modelUrl(p.file));g.computeVertexNormals();geometry.set(p.id,g)}
const nodes=new Map();for(const n of manifest.nodes){const group=new THREE.Group();group.position.fromArray(n.position);if(n.id==='leader')group.position.x=100;if(n.id==='follower')group.position.x=-500;group.rotation.set(...n.rotation.map(THREE.MathUtils.degToRad));if(n.joint!==null)group.rotation.z=THREE.MathUtils.degToRad(manifest.home[n.joint]*(n.factor??1)+(n.offset??0));nodes.set(n.id,group);(n.parent?nodes.get(n.parent):scene).add(group)}

function mat(p,robot){
 const printed=p.kind==='print';
 let color=robot==='leader'?0x599be8:0xf7b34d,metalness=.13,roughness=.4;
 if(!printed){color=0xb9c8d7;metalness=.75;roughness=.3;if(p.id.includes('PCB')||p.id.includes('chip')||p.id.includes('connectors')){color=0x31b48e;metalness=.2}if(p.id.includes('magnet'))color=0xda8195;if(p.id.includes('servo')){color=0x5b6679;metalness=.3}}
 return new THREE.MeshStandardMaterial({color,metalness,roughness,side:THREE.DoubleSide,transparent:true});
}

const objects=manifest.instances.map((entry,index)=>{
 const part=partById.get(entry.part),mesh=new THREE.Mesh(geometry.get(entry.part),mat(part,entry.robot));
 mesh.position.fromArray(entry.position);mesh.rotation.set(...entry.rotation.map(THREE.MathUtils.degToRad));
 nodes.get(entry.node).add(mesh);
 const ghost=new THREE.Mesh(geometry.get(entry.part),new THREE.MeshBasicMaterial({color:entry.robot==='leader'?0x88c6ff:0xffd380,transparent:true,opacity:.18,wireframe:true,depthWrite:false}));
 ghost.position.copy(mesh.position);ghost.rotation.copy(mesh.rotation);nodes.get(entry.node).add(ghost);ghost.visible=false;
 return {index,entry,part,mesh,ghost,target:mesh.position.clone(),rot:mesh.rotation.clone(),center:new THREE.Vector3()};
});
scene.updateMatrixWorld(true);for(const o of objects){new THREE.Box3().setFromObject(o.mesh).getCenter(o.center)}

const steps=[];
function add(ids,chapter,label,instruction,joint,robot,duration){steps.push({ids,chapter,label,instruction,joint,robot,duration})}
add([19],'LEADER / FOUNDATION','Base · encoder leader','Place the printed leader base and clamp it before using the handle.',0,'leader',1.65);
for(let j=0;j<6;j++){
 const b=26+11*j,axis=JOINTS[j],next=20+j;
 add([b],`LEADER / J${j+1} ${axis}`,'Encoder cartridge',`Seat the printed cartridge on the stationary side of J${j+1}.`,j,'leader',1.65);
 add([b+5,b+6,b+7],`LEADER / J${j+1} ${axis}`,'AS5600 sensor PCB','Insert the PCB with its sensing chip facing the future magnet. Secure with M2×4.',j,'leader',1.65);
 add([b+9],`LEADER / J${j+1} ${axis}`,'Rear 688ZZ bearing','Press the 8 × 16 × 5 mm bearing into the rear pocket; not a 608.',j,'leader',1.65);
 add([b+2],`LEADER / J${j+1} ${axis}`,'Rear bearing cap','Close the rear bearing pocket using M2×6 screws.',j,'leader',1.65);
 add([b+8],`LEADER / J${j+1} ${axis}`,'Front 688ZZ bearing','Press the second 688ZZ bearing into the front pocket.',j,'leader',1.65);
 add([b+3],`LEADER / J${j+1} ${axis}`,'Encoder rotor','Slide the rotor through both bearings; it must turn freely.',j,'leader',1.65);
 add([b+1],`LEADER / J${j+1} ${axis}`,'Front bearing cap','Close the front bearing pocket without preloading the rotor.',j,'leader',1.65);
 add([b+4],`LEADER / J${j+1} ${axis}`,'Magnet cup','Key the cup onto the rotor; retain with the axial M3 fastener.',j,'leader',1.65);
 add([b+10],`LEADER / J${j+1} ${axis}`,'Diametric magnet','Seat the Ø6 × 2 mm magnet facing the AS5600 chip.',j,'leader',1.65);
 add([next],`LEADER / J${j+1} ${axis}`,['Shoulder link','Upper-arm link','Forearm link','Wrist pitch/roll body','Handle','Trigger'][j],`Mate the printed ${['shoulder','upper arm','forearm','wrist body','handle','trigger'][j]} to J${j+1}; secure the cartridge tabs and rotor link.`,j,'leader',1.65);
}
const followerOrder=[
 [6,'Follower base','Set and clamp the printed base.'],[0,'MG996R · base axis','Seat servo 1 in its tab mount; use four M3×12 fasteners.'],[13,'25T horn · base axis','Center the servo, fit the round horn and its center screw.'],[7,'Shoulder link','Mate the shoulder to the base horn; four M3×8 link screws.'],
 [1,'MG996R · shoulder','Seat servo 2 in the shoulder mount.'],[14,'25T horn · shoulder','Attach the centered 25T horn at the shoulder axis.'],[8,'Upper-arm link','Mate the upper arm to the shoulder horn.'],
 [2,'MG996R · elbow','Seat servo 3 in the upper-arm mount.'],[15,'25T horn · elbow','Attach its horn after centering the servo.'],[9,'Forearm link','Mate the forearm to the elbow horn.'],
 [3,'MG996R · wrist pitch','Seat servo 4 in the forearm mount.'],[16,'25T horn · wrist pitch','Attach the wrist-pitch horn.'],[10,'Wrist pitch/roll body','Mate the wrist body to the forearm.'],
 [4,'MG996R · wrist roll','Seat servo 5 in the wrist mount.'],[17,'25T horn · wrist roll','Attach the wrist-roll horn.'],[11,'Gripper body','Mate the gripper body to the wrist.'],
 [5,'MG996R · jaw','Seat servo 6 at the jaw drive.'],[18,'25T horn · jaw','Attach the gripper horn.'],[12,'Moving jaw','Mate the moving jaw to the gripper body.']
];
for(let k=0;k<followerOrder.length;k++){const [ix,label,instruction]=followerOrder[k];add([ix],`FOLLOWER / ${['BASE','SHOULDER','ELBOW','WRIST PITCH','WRIST ROLL','GRIP'][Math.min(5,Math.floor(Math.max(k-1,0)/3))]}`,label,instruction,Math.min(5,Math.floor(Math.max(k-1,0)/3)),'follower',(FOLLOWER_END-FOLLOWER_START)/19)}
let cursor=INTRO;for(const s of steps){if(s.robot==='follower'&&cursor<FOLLOWER_START)cursor=FOLLOWER_START;s.start=cursor;s.end=cursor+s.duration;cursor=s.end}
const stepByMesh=new Map();for(let i=0;i<steps.length;i++)for(const ix of steps[i].ids)stepByMesh.set(ix,i);
const leaderFocus=Array.from({length:6},(_,j)=>objects[26+11*j].center.clone());
const followerFocus=[0,1,2,3,4,5].map(ix=>objects[ix].center.clone());
const CAM_DIR=new THREE.Vector3(0.75,-1.18,.8).normalize();
function smooth(x){x=THREE.MathUtils.clamp(x,0,1);return x*x*(3-2*x)}
function offset(ix){const o=objects[ix],small=o.part.kind==='hardware'||o.entry.part.includes('cap')||o.entry.part.includes('cup');const a=(ix*2.3999632297)%(Math.PI*2);return new THREE.Vector3(Math.cos(a)*(small?82:145),Math.sin(a)*(small?75:125),small?70:120)}
function setHud(chapter,label,instruction,counter,t){$('#chapter').textContent=chapter;$('#part').textContent=label;$('#instruction').textContent=instruction;$('#counter').textContent=counter;$('#clock').textContent=`${String(Math.floor(t/60)).padStart(2,'0')}:${String(Math.floor(t%60)).padStart(2,'0')} / 03:00`;$('#bar').style.width=`${t/DURATION*100}%`}
function cameraAt(focus,distance,orbit=0){camera.position.copy(focus).add(CAM_DIR.clone().applyAxisAngle(new THREE.Vector3(0,0,1),orbit).multiplyScalar(distance));camera.lookAt(focus)}
function renderAt(rawTime){
 const t=THREE.MathUtils.clamp(Number(rawTime)||0,0,DURATION-1/24),intro=t<INTRO,transition=t>=LEADER_END&&t<FOLLOWER_START,final=t>=FOLLOWER_END;
 $('.panel').style.display=intro||final?'none':'block';
 $('#status').innerHTML=final?'BOTH 3D ASSEMBLIES COMPLETE<br>Pi 4B → two USB ESP32 boards · external 6 V servo power':intro?'ACTUAL CONVERTED STL GEOMETRY<br>One-by-one assembly into recorded CAD positions':'Actual converted STL geometry<br>Leader L1 + MG996R follower R3';
 let active=-1;for(let i=0;i<steps.length;i++){if(t>=steps[i].start&&t<steps[i].end){active=i;break}}
 for(const o of objects){
  const si=stepByMesh.get(o.index),st=steps[si],p=si===undefined?0:smooth((t-st.start)/Math.min(.92,st.duration*.65));
  o.ghost.visible=active===si&&t>=st.start&&t<st.start+st.duration*.72;
  if(intro){o.mesh.visible=true;o.mesh.position.copy(o.target);o.mesh.rotation.copy(o.rot);o.mesh.material.opacity=.4}
  else if(si===undefined||t<st.start){o.mesh.visible=false;o.mesh.material.opacity=1}
  else{o.mesh.visible=true;o.mesh.position.copy(o.target).addScaledVector(offset(o.index),1-p);o.mesh.rotation.copy(o.rot);o.mesh.rotation.z+=(1-p)*.45;o.mesh.material.opacity=.32+.68*p}
  if(!intro&&!final&&!transition&&o.entry.robot!==(t<FOLLOWER_START?'leader':'follower')){o.mesh.visible=false;o.ghost.visible=false}
 }
 if(intro){cameraAt(new THREE.Vector3(-150,-110,130),1700,-.13);setHud('ACTUAL STL ASSEMBLIES','Leader + follower','Every printed part and purchased reference mesh moves into its recorded 3D CAD position.','92 mesh instances · 80 physical assembly steps',t)}
 else if(transition){const p=smooth((t-LEADER_END)/(FOLLOWER_START-LEADER_END));for(const o of objects)if(o.entry.robot==='follower'){o.mesh.visible=true;o.mesh.material.opacity=.18;o.mesh.position.copy(o.target)}cameraAt(new THREE.Vector3(THREE.MathUtils.lerp(400,0,p),-70,135),THREE.MathUtils.lerp(690,1200,p));setHud('LEADER COMPLETE','Next: MG996R follower','Six encoder joints built. Now the six positional servos and metal horns assemble on the follower.','Leader: 37 printed pieces + sensors, bearings, magnets',t)}
 else if(final){for(const o of objects){o.mesh.visible=true;o.mesh.material.opacity=1;o.mesh.position.copy(o.target);o.mesh.rotation.copy(o.rot);o.ghost.visible=false}cameraAt(new THREE.Vector3(-150,-110,130),1700,(t-FOLLOWER_END)*.004-.13);setHud('BOTH 3D ASSEMBLIES COMPLETE','Bench-fit before power','Pi 4B → USB leader ESP32 + USB follower ESP32. The six MG996R servos need a separate 6 V supply and common ground.','Nominal CAD animation · physical fit and travel not yet validated',t)}
 else if(active>=0){const s=steps[active],o=objects[s.ids[0]],focus=s.robot==='leader'?leaderFocus[s.joint]:followerFocus[s.joint],dist=(o.part.kind==='print'&&!o.entry.part.includes('cartridge')&&!o.entry.part.includes('cap'))?410:260;cameraAt(focus,dist,-.12);indicator.visible=true;indicator.position.copy(o.center);indicator.quaternion.copy(camera.quaternion);indicator.scale.setScalar(1+.06*Math.sin(t*8));setHud(s.chapter,s.label,s.instruction,`${active+1} / ${steps.length} physical assembly steps`,t)}
 else{cameraAt(new THREE.Vector3(400,-90,135),750);setHud('LEADER COMPLETE','Encoder joints assembled','All six leader modules are in their modeled positions.','Moving to follower',t)}
 indicator.visible=active>=0&&!intro&&!final&&!transition;
 scene.updateMatrixWorld(true);renderer.render(scene,camera);return true;
}
ready.remove();window.renderAt=renderAt;window.assemblyReady=true;renderAt(0);
if(!new URLSearchParams(location.search).has('capture')){
 let began=performance.now(),pausedAt=null;
 function play(now){if(pausedAt===null)renderAt(((now-began)/1000)%DURATION);requestAnimationFrame(play)}
 window.addEventListener('keydown',e=>{if(e.code==='Space'){e.preventDefault();if(pausedAt===null)pausedAt=performance.now();else{began+=performance.now()-pausedAt;pausedAt=null}}});
 requestAnimationFrame(play);
}
