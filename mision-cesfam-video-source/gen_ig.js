const { chromium } = require('playwright');
const path = require('path');
const VX=40, VY=600, VW=1000, VH=806, R=40;
const logo=(cx,cy,size)=>{const k=size/220,x=cx-110*k,y=cy-110*k;return `<g transform="translate(${x},${y}) scale(${k})"><rect x="0" y="0" width="220" height="220" rx="56" fill="#1f8a70"/><rect x="44" y="58" width="132" height="120" rx="18" fill="#fff"/><rect x="44" y="58" width="132" height="34" rx="18" fill="#f0a924"/><rect x="44" y="76" width="132" height="16" fill="#f0a924"/><rect x="74" y="42" width="14" height="32" rx="7" fill="#fff"/><rect x="132" y="42" width="14" height="32" rx="7" fill="#fff"/><path d="M78 134 L102 158 L144 112" fill="none" stroke="#1f8a70" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/><path d="M188 20 L194 36 L210 42 L194 48 L188 64 L182 48 L166 42 L182 36 Z" fill="#ffd166"/></g>`};
const T=(x,y,t,size,fill,w=700,anchor='middle')=>`<text x="${x}" y="${y}" text-anchor="${anchor}" font-family="Poppins" font-weight="${w}" font-size="${size}" fill="${fill}">${t}</text>`;
function frame(bg,dark){
  const hole=`M${VX+R} ${VY} H${VX+VW-R} A${R} ${R} 0 0 1 ${VX+VW} ${VY+R} V${VY+VH-R} A${R} ${R} 0 0 1 ${VX+VW-R} ${VY+VH} H${VX+R} A${R} ${R} 0 0 1 ${VX} ${VY+VH-R} V${VY+R} A${R} ${R} 0 0 1 ${VX+R} ${VY} Z`;
  const ink=dark?'#ffffff':'#1d2b29', sub=dark?'#bfe3d6':'#1f8a70';
  return `<path fill-rule="evenodd" d="M0 0 H1080 V1920 H0 Z ${hole}" fill="${bg}"/><path d="${hole}" fill="none" stroke="${dark?'#2a7a66':'#d6e3df'}" stroke-width="3"/>`+
    logo(400,1500,64)+T(448,1494,'Misión CESFAM',38,ink,700,'start')+T(448,1530,'Mi Hora, Tu Oportunidad',24,sub,600,'start');
}
function head(kick,lines,hl,dark,sub){
  let s=''; const ink=dark?'#ffffff':'#1d2b29'; let y=sub?350:(lines.length===1?470:420);
  if(kick){s+=`<rect x="${540-(kick.length*13+40)}" y="${y-150}" width="${kick.length*26+80}" height="56" rx="28" fill="#1f8a70"/>`+T(540,y-111,kick,28,'#fff',700);}
  lines.forEach((l,i)=>{ if(hl&&l.includes(hl)) s+=`<text x="540" y="${y+i*92}" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="80" fill="${ink}">${l.replace(hl,`<tspan style="text-decoration:none">${hl}</tspan>`)}</text>`; else s+=T(540,y+i*92,l,80,ink,700); });
  if(sub) s+=T(540,y+lines.length*92-10,sub,34,'#1f8a70',600);
  return s;
}
const segs={
 intro:{bg:'#fff8ee',kick:'',lines:['¿Ha esperado semanas','por una hora?']},
 sting:{bg:'#155c4b',dark:true,kick:'',lines:[]},
 jorge:{bg:'#eef5f2',kick:'AVISO',lines:['Don Jorge no podrá ir','y avisa a tiempo.']},
 cancel:{bg:'#eef5f2',kick:'RESCATE DE HORAS',lines:['Su hora queda libre…']},
 camila:{bg:'#fff8ee',kick:'LISTA DE ESPERA',lines:['…y llega a quien','la esperaba.']},
 assigned:{bg:'#eef5f2',kick:'¡HORA RESCATADA!',lines:['La hora no se perdió.']},
 climax:{bg:'#fff8ee',kick:'',lines:['Mi Hora,','Tu Oportunidad.'],sub:'Una hora liberada a tiempo, una persona atendida.'},
};
(async()=>{
  const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:1080,height:1920}});
  const shot=async(svg,file)=>{await pg.setContent(`<html><body style="margin:0;background:transparent"><svg width="1080" height="1920" viewBox="0 0 1080 1920" xmlns="http://www.w3.org/2000/svg">${svg}</svg></body></html>`); await pg.waitForTimeout(80); await pg.screenshot({path:path.join(__dirname,'ig',file),omitBackground:true});};
  for(const [n,o] of Object.entries(segs)){ await shot(frame(o.bg,o.dark),`frame_${n}.png`); await shot(head(o.kick,o.lines,null,o.dark,o.sub),`text_${n}.png`); }
  // end card (full frame)
  let e=`<rect width="1080" height="1920" fill="#eef5f2"/><circle cx="120" cy="1500" r="420" fill="#1f8a70" opacity=".08"/><circle cx="980" cy="300" r="260" fill="#f0a924" opacity=".12"/>`;
  e+=logo(540,520,200)+`<text x="540" y="770" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="96" fill="#1d2b29"><tspan fill="#1f8a70">Misión</tspan> CESFAM</text>`;
  e+=`<rect x="${540-300}" y="812" width="600" height="30" fill="#f0a924" opacity=".55"/>`+T(540,838,'Mi Hora, Tu Oportunidad',52,'#1d2b29',700);
  e+=T(540,990,'Si no puede asistir,',58,'#1d2b29',700)+T(540,1062,'avise con tiempo.',58,'#1d2b29',700);
  e+=`<rect x="290" y="1150" width="500" height="96" rx="48" fill="#1f8a70"/>`+T(540,1212,'🔗 Link en la bio',40,'#fff',700);
  e+=T(540,1310,'Juego educativo gratuito · En el navegador',30,'#5e6e6b',600);
  e+=T(540,1440,'Prototipo educativo con casos ficticios.',24,'#7a8a87',500)+T(540,1474,'No reemplaza la atención médica.',24,'#7a8a87',500);
  await shot(e,'endcard.png');
  await b.close(); console.log('ok');
})();
