import {chromium} from '@playwright/test';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdir,unlink} from 'node:fs/promises';
import {resolve} from 'node:path';

const output=resolve('../videos/thenar-real-3d-assembly-180s.mp4');
const rawDir=resolve('../videos/.assembly-capture');
await mkdir(rawDir,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
const context=await browser.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1,recordVideo:{dir:rawDir,size:{width:1920,height:1080}}});
const startWall=Date.now();
const page=await context.newPage();
page.on('pageerror',error=>console.error('Browser error:',error.message));
await page.goto('http://127.0.0.1:5174/assembly-video.html?capture=1');
await page.waitForFunction(()=>window.assemblyReady,{timeout:60000});
const leadIn=(Date.now()-startWall)/1000;
await page.evaluate(()=>{
  const started=performance.now();
  function tick(now){const t=(now-started)/1000;window.renderAt(Math.min(t,179.96));if(t<180.2)requestAnimationFrame(tick)}
  requestAnimationFrame(tick);
});
console.log(`3D capture started · loading lead-in ${leadIn.toFixed(2)}s`);
for(let s=15;s<=180;s+=15){await page.waitForTimeout(15000);console.log(`${s}s / 180s captured`)}
const raw=await page.video().path();
await context.close();await browser.close();
const ffmpeg=spawn('ffmpeg',['-y','-ss',leadIn.toFixed(3),'-i',raw,'-t','180','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',output],{stdio:['ignore','ignore','pipe']});
ffmpeg.stderr.on('data',()=>{});
const [code]=await once(ffmpeg,'close');
if(code!==0)throw new Error(`ffmpeg exited ${code}`);
await unlink(raw);
console.log(`Rendered ${output}`);
