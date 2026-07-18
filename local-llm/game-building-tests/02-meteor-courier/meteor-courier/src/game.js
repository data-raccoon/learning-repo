
(() => {
const C=window.GAME_CONFIG,L=window.GAME_LEVELS,canvas=document.querySelector('#game'),ctx=canvas.getContext('2d');
const ui={score:document.querySelector('#score'),lives:document.querySelector('#lives'),level:document.querySelector('#level'),overlay:document.querySelector('#overlay'),message:document.querySelector('#message'),start:document.querySelector('#start-btn')};
const keys=new Set(); let s,raf,last=0;
const rnd=(a,b)=>a+Math.random()*(b-a),dist=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
function level(){return L[s.levelIndex]}
function entity(r){return{x:rnd(r,canvas.width-r),y:rnd(r,canvas.height-r),r}}
function populate(){s.orbs=Array.from({length:level().orb_count},()=>entity(9));s.meteors=Array.from({length:level().meteor_count},()=>({...entity(rnd(13,24)),vx:rnd(-1,1)*level().meteor_speed,vy:rnd(-1,1)*level().meteor_speed}))}
function reset(){s={running:false,paused:false,score:0,lives:3,levelIndex:0,player:{x:canvas.width/2,y:canvas.height/2,r:13},orbs:[],meteors:[],invulnerable:0};populate();render();show(C.intro,C.start_label)}
function start(){s.running=true;s.paused=false;ui.overlay.hidden=true;last=performance.now();cancelAnimationFrame(raf);raf=requestAnimationFrame(loop);render()}
function show(text,label){ui.message.textContent=text;ui.start.textContent=label;ui.overlay.hidden=false}
function collect(){s.score++;s.orbs[0]=entity(9);if(s.score>=level().target_score)advance();render()}
function hit(){if(!s.running||s.invulnerable>0)return;s.lives--;s.invulnerable=1;s.player.x=canvas.width/2;s.player.y=canvas.height/2;if(s.lives<=0){s.running=false;show(C.game_over,C.start_label)}render()}
function advance(){if(s.levelIndex===L.length-1){s.running=false;show(C.victory,C.start_label);return}s.levelIndex++;s.score=0;populate()}
function update(dt){if(!s.running||s.paused)return;const p=s.player,v=230;if(keys.has('arrowleft')||keys.has('a'))p.x-=v*dt;if(keys.has('arrowright')||keys.has('d'))p.x+=v*dt;if(keys.has('arrowup')||keys.has('w'))p.y-=v*dt;if(keys.has('arrowdown')||keys.has('s'))p.y+=v*dt;p.x=Math.max(p.r,Math.min(canvas.width-p.r,p.x));p.y=Math.max(p.r,Math.min(canvas.height-p.r,p.y));s.invulnerable=Math.max(0,s.invulnerable-dt);
s.meteors.forEach(m=>{m.x+=m.vx*dt;m.y+=m.vy*dt;if(m.x<m.r||m.x>canvas.width-m.r)m.vx*=-1;if(m.y<m.r||m.y>canvas.height-m.r)m.vy*=-1;if(dist(p,m)<p.r+m.r)hit()});
for(let i=0;i<s.orbs.length;i++)if(dist(p,s.orbs[i])<p.r+s.orbs[i].r){s.orbs.unshift(s.orbs.splice(i,1)[0]);collect();break}}
function circle(e,color){ctx.beginPath();ctx.arc(e.x,e.y,e.r,0,Math.PI*2);ctx.fillStyle=color;ctx.shadowColor=color;ctx.shadowBlur=14;ctx.fill();ctx.shadowBlur=0}
function render(){ctx.clearRect(0,0,canvas.width,canvas.height);ctx.fillStyle=C.background_color;ctx.fillRect(0,0,canvas.width,canvas.height);for(let i=0;i<70;i++){ctx.fillStyle='#ffffff55';ctx.fillRect((i*83)%canvas.width,(i*47)%canvas.height,1,1)}s.orbs.forEach(o=>circle(o,C.orb_color));s.meteors.forEach(m=>circle(m,C.meteor_color));if(s.invulnerable<=0||Math.floor(s.invulnerable*10)%2===0)circle(s.player,C.ship_color);ui.score.textContent=`${s.score}/${level().target_score}`;ui.lives.textContent=String(s.lives);ui.level.textContent=`${s.levelIndex+1}: ${level().name}`}
function loop(now){const dt=Math.min(.033,(now-last)/1000||0);last=now;update(dt);render();if(s.running)raf=requestAnimationFrame(loop)}
addEventListener('keydown',e=>{const k=e.key.toLowerCase();keys.add(k);if(k==='p')s.paused=!s.paused;if(k==='r'){reset();start()}});addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()));ui.start.addEventListener('click',()=>{reset();start()});reset();
window.__courierTest={start,snapshot:()=>JSON.parse(JSON.stringify(s)),step:update,keydown:k=>keys.add(k),keyup:k=>keys.delete(k),collect,hit,advance,reset};
})();
