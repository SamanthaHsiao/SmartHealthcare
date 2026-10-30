const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const FPS = 30;
(async () => {
  const mode = process.argv[2];
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + path.resolve(__dirname, 'story4.html'));
  await pg.evaluate(async () => { await document.fonts.load('700 40px Poppins'); await document.fonts.load('500 40px Poppins'); await document.fonts.load('600 40px Poppins'); await document.fonts.ready;
    const srcs=['qr_cup.png','shots/title.png','shots/patient1.png','shots/appt2.png','shots/bonus_board.png','shots/d1_after.png','shots/bonus_modal.png'];
    window._pre=await Promise.all(srcs.map(src=>new Promise(res=>{const i=new Image(); i.onload=()=>i.decode().then(()=>res(i),()=>res(i)); i.onerror=()=>res(null); i.src=src;})));
  });
  if (mode === 'stills') {
    for (const spec of process.argv.slice(3)) {
      const [n, t] = spec.split('@');
      await pg.evaluate(([n, t]) => { setScene(n); render(+t); }, [n, t]); await pg.waitForTimeout(150);
      await pg.screenshot({ path: path.join(__dirname, `s3_${n}_${t}.png`) });
    }
  } else {
    for (const n of process.argv.slice(3)) {
      const dur = await pg.evaluate(n => { setScene(n); return 0; }, n);
      const D = {intro:4.5,sting:3.5,bridge:2,day1:5,jorge:4,cancel:6,camila:4,assigned:3,climax:4,teaserA:3,teaserB:3,core:3,play:5,outro:8}[n];
      const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', path.join(__dirname, `st4_${n}.mp4`)], { stdio: ['pipe', 'inherit', 'inherit'] });
      for (let i = 0; i < Math.round(D * FPS); i++) {
        await pg.evaluate(t => render(t), i / FPS);
        const buf = await pg.screenshot({ type: 'png' });
        if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      }
      ff.stdin.end(); await new Promise(r => ff.on('close', r));
      console.log('rendered', n);
    }
  }
  console.log('errors', errs.length ? errs : 'none');
  await b.close();
})();
