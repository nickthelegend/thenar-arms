import {chromium} from '@playwright/test';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';

const FPS=18,DURATION=180,FRAMES=FPS*DURATION;
const output=resolve('../videos/thenar-real-3d-assembly-180s.mp4');
await mkdir(resolve('../videos'),{recursive:true});
const browser=await chromium.launch({headless:true,args:['--disable-dev-shm-usage']});
const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
page.on('pageerror',error=>console.error('Browser error:',error.message));
await page.goto('http://127.0.0.1:5174/assembly-video.html?capture=1');
await page.waitForFunction(()=>window.assemblyReady,{timeout:60000});
const ffmpeg=spawn('ffmpeg',['-y','-f','image2pipe','-vcodec','mjpeg','-framerate',String(FPS),'-i','pipe:0','-an','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','fast','-movflags','+faststart',output],{stdio:['pipe','ignore','pipe']});
ffmpeg.stderr.on('data',()=>{});
const started=Date.now();
for(let frame=0;frame<FRAMES;frame++){
 await page.evaluate(t=>window.renderAt(t),frame/FPS);
 const jpg=await page.screenshot({type:'jpeg',quality:89});
 if(!ffmpeg.stdin.write(jpg))await once(ffmpeg.stdin,'drain');
 if(frame%180===0)console.log(`${Math.floor(frame/FPS)}s / 180s · ${Math.round((Date.now()-started)/1000)}s elapsed`);
}
ffmpeg.stdin.end();
const [exitCode]=await once(ffmpeg,'close');
await browser.close();
if(exitCode!==0)throw new Error(`ffmpeg exited ${exitCode}`);
console.log(`Rendered ${FRAMES} real 3D frames: ${output}`);
