import { chromium } from "playwright-core";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "..", "assets", "cards");
fs.mkdirSync(OUT, { recursive: true });
const cards = {
  title: `<!doctype html><html><head><meta charset=utf-8><style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@600;700&display=swap');
html,body{margin:0;width:1920px;height:1080px;background:#07090f;color:#e8ecf7;font-family:IBM Plex Sans,sans-serif}
.wrap{padding:120px 96px}
.k{color:#a78bfa;letter-spacing:.2em;text-transform:uppercase;font-size:24px;font-weight:600}
h1{font-size:88px;line-height:1.05;letter-spacing:-.03em;margin:28px 0 24px;width:1200px}
.sub{font-size:32px;color:#9aa3b8;width:980px;line-height:1.35}
.badge{position:fixed;left:96px;bottom:64px;color:#6b7280;font-size:22px}
</style></head><body><div class=wrap>
<div class=k>HOOK</div>
<h1>Frontier models still<br>fail plain Python.</h1>
<p class=sub>Not olympiad algorithms — the class body. PyScope hardens CPython 3.13 LEGB traps.</p>
<div class=badge>PyScope · micro1 Eval Hackathon · LIVE</div>
</div></body></html>`,
  arch: `<!doctype html><html><head><meta charset=utf-8><style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@600;700&family=IBM+Plex+Mono:wght@500&display=swap');
html,body{margin:0;width:1920px;height:1080px;background:#07090f;color:#e8ecf7;font-family:IBM Plex Sans,sans-serif}
.wrap{padding:100px 96px;display:flex;gap:48px}
.left{flex:1}
.k{color:#a78bfa;letter-spacing:.2em;text-transform:uppercase;font-size:24px;font-weight:600}
h1{font-size:64px;line-height:1.05;letter-spacing:-.03em;margin:24px 0 18px;width:820px}
.sub{font-size:28px;color:#9aa3b8;width:780px;line-height:1.35}
.arch{width:860px;display:grid;gap:16px}
.card{border-radius:16px;border:1px solid #242a44;background:linear-gradient(180deg,#161a2b,#101424);padding:22px 26px}
.t{font-family:IBM Plex Mono,monospace;font-size:18px;color:#22d3ee}
.h{font-size:30px;font-weight:700;margin-top:6px}
.d{font-size:22px;color:#9aa3b8;margin-top:8px;line-height:1.35}
.badge{position:fixed;left:96px;bottom:64px;color:#6b7280;font-size:22px}
</style></head><body><div class=wrap>
<div class=left>
<div class=k>ARCHITECTURE</div>
<h1>Probe → harden →<br>pass@1.</h1>
<p class=sub>Oracle 10/10 · 3 trials · temp 0 · automatic JSON graders.</p>
</div>
<div class=arch>
<div class=card><div class=t>tasks/</div><div class=h>10 LEGB traps</div><div class=d>listcomp · NameError · PEP 695 · walrus</div></div>
<div class=card><div class=t>graders/</div><div class=h>JSON exact match</div><div class=d>Oracle ten of ten · unittest guards</div></div>
<div class=card><div class=t>pass@1</div><div class=h>Wonder 6.7% · Spark 13.3% · Beam 76.7%</div><div class=d>Measured matrix on the results page</div></div>
</div>
</div><div class=badge>PyScope · Green Robin Labs</div></body></html>`,
  outro: `<!doctype html><html><head><meta charset=utf-8><style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@600;700&family=IBM+Plex+Mono:wght@500&display=swap');
html,body{margin:0;width:1920px;height:1080px;background:#07090f;color:#e8ecf7;font-family:IBM Plex Sans,sans-serif;display:flex;align-items:center;justify-content:center;text-align:center}
.k{color:#a78bfa;letter-spacing:.2em;text-transform:uppercase;font-size:24px;font-weight:600;margin-bottom:18px}
h1{font-size:110px;margin:0 0 12px;letter-spacing:-.03em}
.tag{font-size:34px;color:#9aa3b8;margin-bottom:28px}
.urls{font-family:IBM Plex Mono,monospace;font-size:28px;color:#22d3ee;line-height:1.7}
.credit{margin-top:36px;font-size:20px;color:#6b7280;letter-spacing:.08em;text-transform:uppercase}
</style></head><body><div>
<div class=k>TRY IT</div>
<h1>PyScope</h1>
<div class=tag>Hardened CPython class-body evals.</div>
<div class=urls>pyscope-evals.vercel.app<br>github.com/dl88jing/micro1-frontier-evals</div>
<div class=credit>Green Robin Labs · micro1 Eval Hackathon</div>
</div></body></html>`,
};
const browser = await chromium.launch({ executablePath: "/usr/bin/google-chrome", args: ["--no-sandbox","--disable-dev-shm-usage"], headless: true });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
for (const [name, html] of Object.entries(cards)) {
  await page.setContent(html, { waitUntil: "networkidle" });
  await page.waitForTimeout(700);
  await page.screenshot({ path: path.join(OUT, `${name}.png`), fullPage: false });
  console.log("wrote", name);
}
await browser.close();
