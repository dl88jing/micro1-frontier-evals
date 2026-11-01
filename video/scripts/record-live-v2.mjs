/**
 * PyScope: record live results page + browser-rendered terminal (real oracle output).
 */
import { chromium } from "playwright-core";
import fs from "fs";
import path from "path";
import { spawnSync } from "child_process";
import { fileURLToPath } from "url";
import { pathToFileURL } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");
const OUT = path.join(ROOT, "captures");
const BASE = process.env.BASE_URL || "https://pyscope-evals.vercel.app";
const TERM = pathToFileURL(path.join(ROOT, "assets", "terminal.html")).href;
const W = 1920, H = 1080;
fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(path.join(OUT, "raw"), { recursive: true });

const CURSOR_JS = `
(() => {
  if (window.__demoCursor) return;
  window.__demoCursor = true;
  const style = document.createElement('style');
  style.textContent = \`
    #__demo_cursor {
      position: fixed; z-index: 2147483647; width: 22px; height: 22px;
      margin-left: -3px; margin-top: -3px; pointer-events: none;
      background: radial-gradient(circle at 30% 30%, #fff 0 18%, #a78bfa 22% 70%, transparent 72%);
      border: 2px solid #fff; border-radius: 50% 50% 50% 0; transform: rotate(-15deg);
      box-shadow: 0 2px 10px rgba(0,0,0,.45), 0 0 0 3px rgba(167,139,250,.35);
      transition: transform 40ms linear;
    }
    #__demo_cursor.clicking { transform: rotate(-15deg) scale(.82); }
    .__demo_ripple {
      position: fixed; z-index: 2147483646; width: 14px; height: 14px; border-radius: 50%;
      border: 2px solid rgba(167,139,250,.9); pointer-events: none;
      transform: translate(-50%,-50%) scale(1); opacity: .9;
      animation: __demo_ripple_anim .55s ease-out forwards;
    }
    @keyframes __demo_ripple_anim {
      to { transform: translate(-50%,-50%) scale(4.2); opacity: 0; }
    }
    #__demo_badge {
      position: fixed; left: 24px; bottom: 24px; z-index: 2147483647;
      background: rgba(11,13,18,.9); border: 1px solid #2a3148; color: #e5e7eb;
      font: 600 14px Inter,system-ui,sans-serif; padding: 8px 14px; border-radius: 999px;
      pointer-events: none;
    }
    #__demo_badge::before {
      content: ''; display: inline-block; width: 8px; height: 8px; border-radius: 50%;
      background: #a78bfa; box-shadow: 0 0 8px #a78bfa; margin-right: 8px; vertical-align: middle;
    }
  \`;
  document.documentElement.appendChild(style);
  const cur = document.createElement('div'); cur.id = '__demo_cursor';
  document.documentElement.appendChild(cur);
  const badge = document.createElement('div'); badge.id = '__demo_badge';
  badge.textContent = 'Live · pyscope-evals.vercel.app';
  document.documentElement.appendChild(badge);
  const move = (nx, ny) => { cur.style.left = nx + 'px'; cur.style.top = ny + 'px'; };
  window.addEventListener('mousemove', (e) => move(e.clientX, e.clientY), true);
  window.addEventListener('mousedown', (e) => {
    cur.classList.add('clicking');
    const r = document.createElement('div'); r.className = '__demo_ripple';
    r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px';
    document.documentElement.appendChild(r);
    setTimeout(() => r.remove(), 600);
  }, true);
  window.addEventListener('mouseup', () => cur.classList.remove('clicking'), true);
  window.__setDemoBadge = (t) => { badge.textContent = t; };
  move(40, 40);
})();
`;

async function humanMove(page, x, y, steps = 22) {
  await page.mouse.move(x, y, { steps });
}

async function withPage(name, fn) {
  const browser = await chromium.launch({
    executablePath: "/usr/bin/google-chrome",
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--hide-scrollbars", "--allow-file-access-from-files"],
    headless: true,
  });
  const context = await browser.newContext({
    viewport: { width: W, height: H },
    deviceScaleFactor: 1,
    recordVideo: { dir: path.join(OUT, "raw"), size: { width: W, height: H } },
  });
  const page = await context.newPage();
  await page.addInitScript(CURSOR_JS);
  console.log(`[${name}] start`);
  try {
    await fn(page);
  } finally {
    const video = page.video();
    await context.close();
    await browser.close();
    if (video) {
      const vpath = await video.path();
      const webm = path.join(OUT, `${name}.webm`);
      const mp4 = path.join(OUT, `${name}.mp4`);
      fs.renameSync(vpath, webm);
      const r = spawnSync("ffmpeg", ["-y", "-i", webm, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "18", "-an", mp4], { encoding: "utf8" });
      if (r.status !== 0) throw new Error("ffmpeg " + name + " " + (r.stderr || "").slice(-300));
      const probe = spawnSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", mp4], { encoding: "utf8" });
      console.log(`[${name}] dur`, probe.stdout.trim());
    }
  }
}

await withPage("01-page", async (page) => {
  await page.goto(BASE + "/", { waitUntil: "networkidle", timeout: 90000 });
  await page.waitForTimeout(2000);
  await page.evaluate(() => window.__setDemoBadge?.("Results page · pass@1 matrix"));
  await humanMove(page, 520, 280, 28);
  await page.waitForTimeout(1400);
  await humanMove(page, 1100, 360, 24);
  await page.waitForTimeout(1200);
  await page.evaluate(() => window.scrollBy({ top: 520, behavior: "smooth" }));
  await page.waitForTimeout(1800);
  await humanMove(page, 700, 480, 20);
  await page.waitForTimeout(1600);
  await page.evaluate(() => window.scrollBy({ top: 700, behavior: "smooth" }));
  await page.waitForTimeout(2000);
  await humanMove(page, 640, 520, 18);
  await page.waitForTimeout(1800);
  await page.evaluate(() => window.scrollBy({ top: 600, behavior: "smooth" }));
  await page.waitForTimeout(2000);
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" }));
  await page.waitForTimeout(1600);
  await humanMove(page, 480, 240, 16);
  await page.waitForTimeout(2000);
  await page.evaluate(() => window.scrollBy({ top: 450, behavior: "smooth" }));
  await page.waitForTimeout(2500);
  await humanMove(page, 820, 460, 20);
  await page.waitForTimeout(3500);
});

await withPage("02-terminal", async (page) => {
  await page.goto(TERM, { waitUntil: "load", timeout: 30000 });
  await page.waitForTimeout(800);
  await page.evaluate(() => window.__setDemoBadge?.("CLI · .venv/bin/python graders/run_all.py"));
  await humanMove(page, 400, 200, 18);
  // Wait until typing finishes
  await page.waitForFunction(() => window.__done === true, { timeout: 180000 });
  await page.waitForTimeout(4000);
  await humanMove(page, 900, 600, 22);
  await page.waitForTimeout(3500);
});

await withPage("03-page-results", async (page) => {
  await page.goto(BASE + "/", { waitUntil: "networkidle", timeout: 90000 });
  await page.waitForTimeout(1500);
  await page.evaluate(() => window.__setDemoBadge?.("Headline · Wonder 6.7% · Spark 13.3% · Beam 76.7%"));
  // Focus on results table area
  await page.evaluate(() => {
    const el = document.querySelector("table") || document.body;
    el.scrollIntoView({ block: "center", behavior: "smooth" });
  });
  await page.waitForTimeout(1800);
  await humanMove(page, 700, 420, 24);
  await page.waitForTimeout(2000);
  await page.evaluate(() => window.scrollBy({ top: 400, behavior: "smooth" }));
  await page.waitForTimeout(1800);
  await humanMove(page, 980, 500, 20);
  await page.waitForTimeout(2500);
  await page.evaluate(() => window.scrollBy({ top: 500, behavior: "smooth" }));
  await page.waitForTimeout(2000);
  await humanMove(page, 560, 380, 18);
  await page.waitForTimeout(3000);
  await page.evaluate(() => window.scrollBy({ top: 350, behavior: "smooth" }));
  await page.waitForTimeout(2500);
  await humanMove(page, 720, 440, 16);
  await page.waitForTimeout(4000);
});

console.log("DONE");
