import {defineConfig} from 'vite';
import {resolve} from 'node:path';

export default defineConfig({
  base:process.env.GITHUB_PAGES==='true'?'/thenar-arms/':'/',
  build:{
    target:'esnext',
    rollupOptions:{
      input:{
        main:resolve(import.meta.dirname,'index.html'),
        assemblyVideo:resolve(import.meta.dirname,'assembly-video.html'),
      },
    },
  },
});
