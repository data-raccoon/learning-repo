"""Build a browser-tested game from a local-Mistral manifest and visual theme.

Large local-model artifacts never enter the calling agent's context. The controller
prints only compact pass/failure status.
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME_DIR = ROOT / "kebab-case-tic-tac-toe"
TARGET = GAME_DIR / "index.html"
KEY_FILE = Path(r"C:\LLMs\config\api_key.txt")
ENDPOINT = "http://127.0.0.1:8081/v1/chat/completions"
MODEL = "ministral-3b-q4"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


MANIFEST_PROMPT = """
Design the presentation copy for a two-player center-start tic-tac-toe browser game.
Return JSON only with exactly these string fields: title, eyebrow, center_instruction,
x_turn, o_turn, x_wins, o_wins, tie, restart_label, help_text, x_color, o_color.
Use concise friendly English. Values x_wins and o_wins must contain {player}; x_turn
and o_turn must also contain {player}. Colors must be six-digit hex values. No URLs,
HTML, Markdown, or extra keys.
""".strip()

CSS_PROMPT = """
Write CSS only for a polished responsive neon/arcade game with this fixed DOM:
main.game-shell; header with .eyebrow and h1; section.scoreboard with two divs;
p.status; div.board containing nine button.cell elements; button.restart; p.help.
Classes .cell.x, .cell.o, .cell.center-required, and .cell.winning must be visually
distinct. Include strong .cell:focus-visible styling and a small-screen media query.
Use var(--x-color) and var(--o-color). No URLs, imports, external assets, Markdown,
or commentary.
""".strip()


def call_local(system: str, prompt: str, max_tokens: int) -> str:
    key = KEY_FILE.read_text(encoding="ascii").strip()
    payload = json.dumps(
        {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        return json.load(response)["choices"][0]["message"]["content"].strip()


def strip_fence(text: str, language: str) -> str:
    match = re.fullmatch(rf"\s*```(?:{language})?\s*(.*?)\s*```\s*", text, re.I | re.S)
    return (match.group(1) if match else text).strip()


def generate_manifest() -> dict[str, str]:
    raw = strip_fence(call_local("You design concise game copy and emit strict JSON.", MANIFEST_PROMPT, 1600), "json")
    data = json.loads(raw)
    fields = {
        "title", "eyebrow", "center_instruction", "x_turn", "o_turn", "x_wins",
        "o_wins", "tie", "restart_label", "help_text", "x_color", "o_color",
    }
    if not isinstance(data, dict) or not fields.issubset(data):
        raise ValueError("MANIFEST_SCHEMA")
    normalized = {key: str(data[key]).strip()[:160] for key in fields}
    if not all(normalized.values()):
        raise ValueError("MANIFEST_EMPTY_VALUE")
    for key, fallback in (("x_color", "#45A3FF"), ("o_color", "#FF4D8D")):
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", normalized[key]):
            normalized[key] = fallback
    for key in ("x_turn", "o_turn", "x_wins", "o_wins"):
        if "{player}" not in normalized[key]:
            normalized[key] = "Player {player}: " + normalized[key]
    return normalized


def generate_css() -> str:
    css = strip_fence(call_local("You are a focused CSS designer.", CSS_PROMPT, 5000), "css")
    if not css or re.search(r"https?://|@import|url\s*\(", css, re.I):
        raise ValueError("CSS_EXTERNAL_ASSET")
    for token in (":focus-visible", ".winning", ".center-required", "@media"):
        if token not in css:
            raise ValueError("CSS_MISSING_" + re.sub(r"\W+", "_", token).strip("_").upper())
    return css


ENGINE = r"""
const config = JSON.parse(document.querySelector('#game-config').textContent);
const cells = [...document.querySelectorAll('button.cell')];
const statusEl = document.querySelector('#status');
const xScoreEl = document.querySelector('#x-score');
const oScoreEl = document.querySelector('#o-score');
const wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
let boardState = Array(9).fill('');
let currentPlayer = 'X';
let scores = {X: 0, O: 0};
let roundActive = true;
let winningLine = [];

function lineFor(player) {
  return wins.find(line => line.every(index => boardState[index] === player)) || [];
}
function isMoveAllowed(index) {
  return roundActive && boardState[index] === '' && (boardState[4] !== '' || index === 4);
}
function message(template, player) { return template.replace('{player}', player); }
function render() {
  cells.forEach((cell, index) => {
    cell.textContent = boardState[index];
    cell.disabled = !isMoveAllowed(index);
    cell.classList.toggle('x', boardState[index] === 'X');
    cell.classList.toggle('o', boardState[index] === 'O');
    cell.classList.toggle('center-required', boardState[4] === '' && index === 4);
    cell.classList.toggle('winning', winningLine.includes(index));
    const state = boardState[index] || (cell.disabled ? 'unavailable' : 'empty');
    cell.setAttribute('aria-label', `Cell ${index + 1}: ${state}`);
  });
  xScoreEl.textContent = String(scores.X);
  oScoreEl.textContent = String(scores.O);
  if (roundActive) statusEl.textContent = boardState[4] === ''
    ? config.center_instruction
    : message(currentPlayer === 'X' ? config.x_turn : config.o_turn, currentPlayer);
}
function finishRound() {
  winningLine = lineFor(currentPlayer);
  if (winningLine.length) {
    roundActive = false;
    scores[currentPlayer] += 1;
    statusEl.textContent = message(currentPlayer === 'X' ? config.x_wins : config.o_wins, currentPlayer);
    return true;
  }
  if (boardState.every(Boolean)) {
    roundActive = false;
    statusEl.textContent = config.tie;
    return true;
  }
  return false;
}
function playMove(index) {
  if (!isMoveAllowed(index)) return;
  boardState[index] = currentPlayer;
  if (!finishRound()) currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
  render();
}
function resetRound() {
  boardState = Array(9).fill(''); currentPlayer = 'X'; roundActive = true; winningLine = [];
  render();
}
cells.forEach((cell, index) => cell.addEventListener('click', () => playMove(index)));
document.querySelector('#restart-btn').addEventListener('click', resetRound);
document.addEventListener('keydown', event => {
  const key = event.key.toLowerCase();
  if (key === 'e') resetRound();
  else if (key === 'w' && currentPlayer === 'X') playMove(4);
  else if (key === 's' && currentPlayer === 'O') playMove(4);
});
render();
"""


SMOKE = r"""
<script>
if (new URLSearchParams(location.search).has('smoke')) addEventListener('load', () => {
  const f=[], c=[...document.querySelectorAll('button.cell')], q=s=>document.querySelector(s);
  const ok=(v,n)=>{if(!v)f.push(n)}, score=s=>Number(q(s).textContent), key=k=>document.dispatchEvent(new KeyboardEvent('keydown',{key:k,bubbles:true}));
  try {
    ok(c.every((x,i)=>i===4?!x.disabled:x.disabled),'INITIAL_GATE'); c[0].click(); ok(!c[0].textContent,'LOCK');
    key('W'); ok(c[4].textContent==='X','W_CENTER'); ok(c.filter(x=>!x.disabled).length===8,'UNLOCK');
    c[0].click(); c[2].click(); c[1].click(); c[6].click();
    ok(score('#x-score')===1&&score('#o-score')===0,'SCORE'); ok(/win/i.test(q('#status').textContent),'STATUS');
    ok(document.querySelectorAll('.winning').length===3,'HIGHLIGHT'); q('#restart-btn').click();
    ok(score('#x-score')===1,'PERSIST'); ok(c.every((x,i)=>i===4?!x.disabled:x.disabled),'RESET_GATE');
    key('e'); key('w'); ok(c[4].textContent==='X','KEY_CASE'); ok(q('#status').getAttribute('aria-live')==='polite','ARIA');
  } catch(e) { f.push('RUNTIME_'+e.name); }
  q('#smoke-result').textContent=f.length?'FAIL:'+f.join(','):'PASS';
});
</script>
"""


def assemble(manifest: dict[str, str], css: str, smoke: bool) -> str:
    cells = "\n".join(f'<button class="cell" data-index="{i}" type="button"></button>' for i in range(9))
    safe_config = json.dumps(manifest, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(manifest['title'])}</title>
<style>:root{{--x-color:{manifest['x_color']};--o-color:{manifest['o_color']}}}{css}</style></head><body>
<main class="game-shell"><header><p class="eyebrow">{html.escape(manifest['eyebrow'])}</p><h1>{html.escape(manifest['title'])}</h1></header>
<section class="scoreboard" aria-label="Scoreboard"><div>Player X <strong id="x-score">0</strong></div><div>Player O <strong id="o-score">0</strong></div></section>
<p id="status" class="status" aria-live="polite"></p><div id="board" class="board" aria-label="Tic-tac-toe board">{cells}</div>
<button id="restart-btn" class="restart" type="button">{html.escape(manifest['restart_label'])}</button><p class="help">{html.escape(manifest['help_text'])}</p>
<output id="smoke-result" hidden>PENDING</output></main><script id="game-config" type="application/json">{safe_config}</script><script>{ENGINE}</script>
{SMOKE if smoke else ''}</body></html>\n"""


def browser_smoke(manifest: dict[str, str], css: str) -> list[str]:
    candidate = GAME_DIR / ".candidate.html"
    candidate.write_text(assemble(manifest, css, True), encoding="utf-8")
    try:
        with tempfile.TemporaryDirectory(prefix="center-lock-edge-") as profile:
            result = subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--no-first-run",
                f"--user-data-dir={profile}", "--virtual-time-budget=1500", "--dump-dom",
                candidate.resolve().as_uri()+"?smoke=1"], capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=45)
        match = re.search(r'<output id="smoke-result"[^>]*>(.*?)</output>', result.stdout, re.S)
        value = html.unescape(match.group(1)).strip() if match else "FAIL:BROWSER_NO_RESULT"
        return [] if value == "PASS" else value.removeprefix("FAIL:").split(",")[:12]
    finally:
        candidate.unlink(missing_ok=True)


def main() -> None:
    GAME_DIR.mkdir(parents=True, exist_ok=True)
    manifest, css = generate_manifest(), generate_css()
    failures = browser_smoke(manifest, css)
    if failures:
        raise SystemExit("FAILED " + ",".join(failures))
    TARGET.write_text(assemble(manifest, css, False), encoding="utf-8")
    print(f"PASS file={TARGET.relative_to(ROOT)} model_tasks=2 browser_tests=12")


if __name__ == "__main__":
    main()
