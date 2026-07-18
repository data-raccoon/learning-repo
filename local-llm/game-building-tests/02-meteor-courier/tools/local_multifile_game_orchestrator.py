"""Build a multi-file game from bounded local-Mistral artifacts and browser-test it."""

from __future__ import annotations

import html
import json
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "meteor-courier"
KEY_FILE = Path(r"C:\LLMs\config\api_key.txt")
ENDPOINT = "http://127.0.0.1:8081/v1/chat/completions"
MODEL = "ministral-3b-q4"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def call_local(system: str, prompt: str, max_tokens: int) -> str:
    key = KEY_FILE.read_text(encoding="ascii").strip()
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }).encode("utf-8")
    request = urllib.request.Request(ENDPOINT, data=payload, method="POST", headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.load(response)["choices"][0]["message"]["content"].strip()


def unfence(text: str, language: str = "") -> str:
    match = re.fullmatch(rf"\s*```(?:{language})?\s*(.*?)\s*```\s*", text, re.I | re.S)
    return (match.group(1) if match else text).strip()


def local_json(prompt: str) -> object:
    for _ in range(2):
        raw = unfence(call_local("Return strict JSON only. Never use Markdown fences.", prompt, 2400), "json")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            prompt = "Your previous JSON was invalid. Return valid JSON only.\n\n" + prompt
    raise ValueError("LOCAL_JSON_INVALID")


def game_manifest() -> dict[str, object]:
    prompt = """Design the identity and presentation for a fast offline canvas game about
a courier ship collecting energy orbs while dodging meteors. Return one JSON object with
exactly: title, subtitle, intro, start_label, controls_help, score_label, lives_label,
level_label, game_over, victory, ship_color, orb_color, meteor_color, background_color.
All are concise strings. Colors are six-digit hex. No HTML, URLs, or Markdown."""
    raw = local_json(prompt)
    if not isinstance(raw, dict):
        raise ValueError("MANIFEST_NOT_OBJECT")
    defaults = {
        "title": "Meteor Courier", "subtitle": "Run the orbital gauntlet",
        "intro": "Collect energy. Dodge everything else.", "start_label": "Launch",
        "controls_help": "Move with WASD or arrow keys · P pauses · R restarts",
        "score_label": "Energy", "lives_label": "Hull", "level_label": "Route",
        "game_over": "Courier lost", "victory": "Delivery complete",
        "ship_color": "#58E1FF", "orb_color": "#FFE66D", "meteor_color": "#FF5D73",
        "background_color": "#070B1B",
    }
    result: dict[str, object] = {}
    for key, fallback in defaults.items():
        value = str(raw.get(key, fallback)).strip()[:180]
        if key.endswith("_color") and not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            value = fallback
        result[key] = value or fallback
    return result


def level_manifest() -> list[dict[str, object]]:
    prompt = """Design four escalating levels for an arcade collection game. Return a JSON
array of four objects with exactly: name (short string), target_score (integer 4..14),
meteor_speed (integer 80..260), meteor_count (integer 2..9), orb_count (integer 1..4).
Difficulty and target_score must increase. JSON only."""
    raw = local_json(prompt)
    if not isinstance(raw, list):
        raise ValueError("LEVELS_NOT_ARRAY")
    fallbacks = [
        {"name": "Low Orbit", "target_score": 4, "meteor_speed": 90, "meteor_count": 2, "orb_count": 2},
        {"name": "Debris Belt", "target_score": 6, "meteor_speed": 130, "meteor_count": 4, "orb_count": 2},
        {"name": "Ion Storm", "target_score": 8, "meteor_speed": 180, "meteor_count": 6, "orb_count": 3},
        {"name": "Final Approach", "target_score": 10, "meteor_speed": 230, "meteor_count": 8, "orb_count": 3},
    ]
    levels: list[dict[str, object]] = []
    for index, fallback in enumerate(fallbacks):
        item = raw[index] if index < len(raw) and isinstance(raw[index], dict) else {}
        levels.append({
            "name": str(item.get("name", fallback["name"]))[:60],
            "target_score": max(4, min(14, int(item.get("target_score", fallback["target_score"])))),
            "meteor_speed": max(80, min(260, int(item.get("meteor_speed", fallback["meteor_speed"])))),
            "meteor_count": max(2, min(9, int(item.get("meteor_count", fallback["meteor_count"])))),
            "orb_count": max(1, min(4, int(item.get("orb_count", fallback["orb_count"])))),
        })
    levels.sort(key=lambda level: (int(level["target_score"]), int(level["meteor_speed"])))
    return levels


BASE_CSS = """
:root{--ship:#58e1ff;--orb:#ffe66d;--meteor:#ff5d73;--space:#070b1b;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--space);color:#f5f7ff;font-family:system-ui,sans-serif}
.game-shell{width:min(94vw,900px);padding:1rem}.topbar,.hud{display:flex;align-items:center;justify-content:space-between;gap:1rem;flex-wrap:wrap}
h1{margin:.15rem 0}.subtitle,.help{opacity:.78}.hud{margin:.8rem 0}.hud strong{color:var(--orb)}
.stage{position:relative}canvas{display:block;width:100%;height:auto;aspect-ratio:3/2;border:1px solid #ffffff2b;border-radius:16px;background:#040713}
.overlay{position:absolute;inset:0;display:grid;place-content:center;text-align:center;padding:2rem;background:#030615c9;border-radius:16px}.overlay[hidden]{display:none}
button{font:inherit;padding:.7rem 1.1rem;border:0;border-radius:999px;background:var(--ship);color:#03101a;font-weight:800;cursor:pointer}
button:focus-visible{outline:3px solid white;outline-offset:4px}.help{text-align:center}@media(max-width:600px){.game-shell{padding:.5rem}.hud{font-size:.9rem}}
""".strip()


def theme_css(manifest: dict[str, object]) -> str:
    prompt = f"""Write an optional CSS enhancement layer for the fixed game selectors:
body, .game-shell, .topbar, h1, .subtitle, .hud, .stage, canvas, .overlay, button, .help.
Create an energetic sci-fi look matching this title: {manifest['title']}.
Do not use URLs, imports, assets, HTML, or Markdown. Return CSS only."""
    css = unfence(call_local("You are a focused CSS designer. Output CSS only.", prompt, 3600), "css")
    if re.search(r"https?://|@import|url\s*\(", css, re.I):
        raise ValueError("THEME_EXTERNAL_ASSET")
    return css


ENGINE = r"""
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
"""


def index_html(manifest: dict[str, object]) -> str:
    e=lambda key:html.escape(str(manifest[key]))
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e('title')}</title><link rel="stylesheet" href="styles.css"></head>
<body><main class="game-shell"><header class="topbar"><div><p class="subtitle">{e('subtitle')}</p><h1>{e('title')}</h1></div></header>
<section class="hud" aria-label="Game status"><span>{e('score_label')}: <strong id="score">0</strong></span><span>{e('lives_label')}: <strong id="lives">3</strong></span><span>{e('level_label')}: <strong id="level">1</strong></span></section>
<div class="stage"><canvas id="game" width="720" height="480" aria-label="Meteor Courier game area"></canvas><div id="overlay" class="overlay"><p id="message">{e('intro')}</p><button id="start-btn" type="button">{e('start_label')}</button></div></div><p class="help">{e('controls_help')}</p><output id="smoke-result" hidden>PENDING</output></main>
<script src="config/game-data.js"></script><script src="src/game.js"></script><script src="smoke.js"></script></body></html>\n"""


SMOKE = r"""
if(new URLSearchParams(location.search).has('smoke'))addEventListener('load',()=>{const f=[],ok=(v,n)=>{if(!v)f.push(n)},t=window.__courierTest,q=s=>document.querySelector(s);try{ok(!!t,'API');t.start();let a=t.snapshot();ok(a.running&&a.lives===3&&a.levelIndex===0,'START');let n=a.score;t.collect();ok(t.snapshot().score===n+1,'COLLECT');t.hit();ok(t.snapshot().lives===2,'HIT');let x=t.snapshot().player.x;t.keydown('arrowright');t.step(.1);t.keyup('arrowright');ok(t.snapshot().player.x>x,'MOVE');t.advance();ok(t.snapshot().levelIndex===1,'LEVEL');t.reset();a=t.snapshot();ok(!a.running&&a.lives===3&&a.levelIndex===0,'RESET');ok(q('#game').width===720,'CANVAS');ok(window.GAME_LEVELS.length===4,'LEVEL_DATA');ok(getComputedStyle(document.body).fontFamily.length>0,'CSS');}catch(e){f.push('RUNTIME_'+e.name)}q('#smoke-result').textContent=f.length?'FAIL:'+f.join(','):'PASS'});
"""


def readme(manifest: dict[str, object], levels: list[dict[str, object]]) -> str:
    prompt=f"""Write a concise README.md for this offline browser game. Include overview,
controls, objective, level table, files, and how to launch by opening index.html. Do not
claim network dependencies. Manifest: {json.dumps(manifest)} Levels: {json.dumps(levels)}
Return Markdown only without an outer code fence."""
    return unfence(call_local("You are a concise technical game-documentation writer.",prompt,3000),"markdown")+"\n"


def write_tree(base: Path, manifest: dict[str, object], levels: list[dict[str, object]], css: str, docs: str) -> None:
    (base/"config").mkdir(parents=True,exist_ok=True);(base/"src").mkdir(parents=True,exist_ok=True)
    (base/"index.html").write_text(index_html(manifest),encoding="utf-8")
    (base/"styles.css").write_text(BASE_CSS+"\n"+css+"\n",encoding="utf-8")
    (base/"config"/"game.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    (base/"config"/"levels.json").write_text(json.dumps(levels,indent=2)+"\n",encoding="utf-8")
    data="window.GAME_CONFIG="+json.dumps(manifest)+";\nwindow.GAME_LEVELS="+json.dumps(levels)+";\n"
    (base/"config"/"game-data.js").write_text(data,encoding="utf-8")
    (base/"src"/"game.js").write_text(ENGINE,encoding="utf-8")
    (base/"smoke.js").write_text(SMOKE,encoding="utf-8")
    (base/"README.md").write_text(docs,encoding="utf-8")


def browser_test(base: Path) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="courier-edge-") as profile:
        result=subprocess.run([str(EDGE),"--headless=new","--disable-gpu","--no-first-run",f"--user-data-dir={profile}","--virtual-time-budget=1800","--dump-dom",(base/"index.html").resolve().as_uri()+"?smoke=1"],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=45)
    match=re.search(r'<output id="smoke-result"[^>]*>(.*?)</output>',result.stdout,re.S)
    value=html.unescape(match.group(1)).strip() if match else "FAIL:BROWSER_NO_RESULT"
    return [] if value=="PASS" else value.removeprefix("FAIL:").split(",")[:12]


def main() -> None:
    manifest,levels=game_manifest(),level_manifest();css=theme_css(manifest);docs=readme(manifest,levels)
    with tempfile.TemporaryDirectory(prefix="meteor-courier-stage-",dir=ROOT) as staging:
        stage=Path(staging);write_tree(stage,manifest,levels,css,docs);failures=browser_test(stage)
        if failures:raise SystemExit("FAILED "+",".join(failures))
        write_tree(TARGET,manifest,levels,css,docs)
    print("PASS directory=meteor-courier files=8 model_tasks=4 browser_tests=10")


if __name__=="__main__":main()
