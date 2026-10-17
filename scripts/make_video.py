"""Produce the NightTwin jury video (docs/video/NightTwin_Walkthrough.mp4).

Pipeline
  1. Neural Indian-English voices (Microsoft Edge neural TTS via `edge-tts`), with word timings.
  2. A real, recorded walk-through of the running dashboard (Playwright + Chrome screencast)
     with a visible cursor, clicks, smooth scrolling and hover tooltips.
  3. Animated title cards (opening hook, chapter cards, closing hook), recorded the same way.
  4. Slides from docs/TwinPulse_Presentation.pdf with a slow camera move.
  5. Burned-in captions from the word timings, a soft music bed under the opening and closing.

Needs: the app running at APP_URL (./run.sh), Google Chrome, ffmpeg, pdftoppm, internet for the voices.
Install: .venv/bin/python -m pip install -r requirements-video.txt
Run:     .venv/bin/python scripts/make_video.py
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from video_script import S as SCRIPT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "video", "NightTwin_Walkthrough.mp4")
WORK = os.path.join(ROOT, "docs", "video", "build")
APP = os.environ.get("APP_URL", "http://localhost:8000")
W, H, FPS = 1920, 1080, 25
VOICES = {"presenter": ("en-IN-PrabhatNeural", "-3%"), "story": ("en-IN-NeerjaExpressiveNeural", "-6%")}
LEAD_IN, TAIL = 0.35, 0.7          # silence before / after each spoken line (seconds)
CHAPTER_SECONDS = 2.6
LOGO_SVG = open(os.path.join(ROOT, "dashboard", "public", "favicon.svg")).read()

# How the voices should say a few things
SAY = [(r"\bCGMs\b", "C G Ms"), (r"\bCGM\b", "C G M"), (r"\bNPH\b", "N P H"), (r"\bFHIR R4\b", "fire R4"), (r"\bFHIR\b", "fire"),
       (r"\bHbA1c\b", "H b A 1 c"), (r"\bDCCT\b", "D C C T"), (r"\bIDF\b", "I D F"), (r"\bDPDP\b", "D P D P"),
       (r"\bCDSCO\b", "C D S C O"), (r"\bABHA\b", "abha"), (r"\bNGO\b", "N G O"), (r"FastAPI", "Fast A P I"),
       (r"LightGBM", "Light G B M"), (r"HUPA-UCM", "HUPA U C M"), (r"T1D-UOM", "T 1 D U O M"), (r"\bPM\b", "P M"),
       (r"\bAM\b", "A M"), (r"\bUK\b", "U K"), (r"NumPy", "Num Pie"), (r"SciPy", "Sci Pie"), (r"scikit-learn", "scikit learn")]


def sh(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                                capture_output=True, text=True).stdout)


# ---------------------------------------------------------------- 1. voices
async def tts(text, role, out_mp3, out_json):
    voice, rate = VOICES[role]
    spoken = text
    for pat, rep in SAY:
        spoken = re.sub(pat, rep, spoken)
    comm = edge_tts.Communicate(spoken, voice, rate=rate, boundary="WordBoundary")
    words = []
    with open(out_mp3, "wb") as f:
        async for ch in comm.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append([ch["offset"] / 1e7, ch["duration"] / 1e7, ch["text"]])
    with open(out_json, "w") as f:
        json.dump(words, f)


async def make_voices(segs):
    for i, s in enumerate(segs):
        if not s["line"]:
            continue
        key = hashlib.sha1((s["voice"] + s["line"]).encode()).hexdigest()[:12]
        s["mp3"] = os.path.join(WORK, "voice", f"{key}.mp3")
        s["words_path"] = s["mp3"].replace(".mp3", ".json")
        if not os.path.exists(s["mp3"]):
            for attempt in range(4):
                try:
                    await tts(s["line"], s["voice"], s["mp3"], s["words_path"])
                    break
                except Exception:  # transient network errors
                    await asyncio.sleep(2 + attempt * 3)
            else:
                raise RuntimeError(f"voice failed for segment {i}")
        s["audio"] = duration(s["mp3"])
        s["words"] = json.load(open(s["words_path"]))
        print(f"voice {i + 1}/{len(segs)}  {s['audio']:.1f}s", flush=True)


# ---------------------------------------------------------------- 2/3. browser recording
CURSOR_JS = r"""
(() => {
  if (window.__ntCursor) return; window.__ntCursor = true;
  const add = () => {
    const c = document.createElement('div');
    c.id = '__nt_cursor';
    c.innerHTML = '<svg width="28" height="28" viewBox="0 0 24 24"><path d="M4 2l15 9-6.5 1.6L16 20l-3 1.4-3.4-7.3L4 18z" fill="#fff" stroke="#0b1022" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    Object.assign(c.style, {position:'fixed', left:'0', top:'0', zIndex: 2147483647, pointerEvents:'none',
      transform:'translate(-100px,-100px)', filter:'drop-shadow(0 3px 6px rgba(0,0,0,.35))', transition:'transform 0s'});
    document.documentElement.appendChild(c);
    document.addEventListener('mousemove', e => { c.style.transform = `translate(${e.clientX - 4}px, ${e.clientY - 2}px)`; }, true);
    document.addEventListener('mousedown', e => {
      const r = document.createElement('div');
      Object.assign(r.style, {position:'fixed', left: (e.clientX - 22) + 'px', top: (e.clientY - 22) + 'px', width:'44px', height:'44px',
        borderRadius:'50%', border:'3px solid rgba(99,102,241,.9)', background:'rgba(99,102,241,.18)', zIndex: 2147483646,
        pointerEvents:'none', transform:'scale(.3)', opacity:'1', transition:'transform .45s ease-out, opacity .55s ease-out'});
      document.documentElement.appendChild(r);
      requestAnimationFrame(() => { r.style.transform = 'scale(1.4)'; r.style.opacity = '0'; });
      setTimeout(() => r.remove(), 650);
    }, true);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', add); else add();
})();
"""


class Recorder:
    def __init__(self, page, session):
        self.page, self.session = page, session
        self.frames = []  # (timestamp, jpeg bytes)
        self.mouse = [W / 2 / 1.2, H / 2 / 1.2]

    async def start(self):
        async def on_frame(ev):
            self.frames.append((ev["metadata"]["timestamp"], base64.b64decode(ev["data"])))
            try:
                await self.session.send("Page.screencastFrameAck", {"sessionId": ev["sessionId"]})
            except Exception:
                pass
        self.session.on("Page.screencastFrame", lambda ev: asyncio.ensure_future(on_frame(ev)))
        await self.session.send("Page.startScreencast", {"format": "jpeg", "quality": 92, "maxWidth": W, "maxHeight": H, "everyNthFrame": 1})

    # --- human-like primitives
    async def move_to(self, x, y, speed=1.0):
        x0, y0 = self.mouse
        dist = ((x - x0) ** 2 + (y - y0) ** 2) ** 0.5
        steps = max(8, int(dist / 18 / speed))
        for k in range(1, steps + 1):
            t = k / steps
            e = t * t * (3 - 2 * t)  # ease in-out
            await self.page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
            await asyncio.sleep(0.014)
        self.mouse = [x, y]

    async def box(self, sel):
        loc = self.page.locator(sel).first
        await loc.wait_for(state="visible", timeout=8000)
        return await loc.bounding_box()

    async def ensure_visible(self, sel):
        """If the element is off-screen, bring it to roughly a third of the way down (keeps context visible)."""
        b = await self.box(sel)
        vh = self.page.viewport_size["height"]
        if b["y"] < 80 or b["y"] + min(b["height"], 300) > vh - 40:
            y = await self.page.evaluate("window.scrollY")
            await self.scroll_to_y(max(0, b["y"] + y - vh * 0.32))

    async def scroll_to_y(self, target):
        await self.page.evaluate("""(t) => new Promise(res => {
            const s = window.scrollY, d = t - s, n = 45; let i = 0;
            const step = () => { i++; const e = i/n < .5 ? 2*(i/n)**2 : 1 - (-2*(i/n)+2)**2/2;
              window.scrollTo({top: s + d*e, behavior: 'instant'}); if (i < n) requestAnimationFrame(step); else res(); };
            requestAnimationFrame(step); })""", target)
        await asyncio.sleep(0.35)

    async def scroll(self, sel):
        y = await self.page.evaluate("(s) => { const el = document.querySelector(s); if (!el) return null;"
                                     " return el.getBoundingClientRect().top + window.scrollY - 96; }", self._css(sel))
        if y is None:
            b = await self.box(sel)
            y = b["y"] + await self.page.evaluate("window.scrollY") - 96
        await self.scroll_to_y(max(0, y))

    @staticmethod
    def _css(sel):
        # plain CSS only for querySelector; Playwright-specific selectors fall back to locator boxes
        return sel if ":has-text" not in sel and ":has(" not in sel else "__no_such__"

    async def hover(self, sel, frac=None):
        await self.ensure_visible(sel)
        b = await self.box(sel)
        x = b["x"] + (b["width"] * frac if frac is not None else min(b["width"] / 2, 260))
        y = b["y"] + min(b["height"] / 2, 120)
        await self.move_to(x, y)
        await asyncio.sleep(0.5)

    async def click(self, sel):
        await self.hover(sel)
        await self.page.mouse.down()
        await asyncio.sleep(0.08)
        await self.page.mouse.up()
        await asyncio.sleep(0.9)

    async def run(self, actions):
        for a in actions:
            kind = a[0]
            try:
                if kind == "goto":
                    await self.page.evaluate("(h) => { window.location.hash = h; }", a[1])
                    await asyncio.sleep(1.3)
                elif kind == "open":
                    await self.page.goto(a[1], wait_until="load", timeout=45000)
                    await asyncio.sleep(0.8)
                elif kind == "wait":
                    await asyncio.sleep(a[1])
                elif kind == "hover":
                    await self.hover(a[1])
                elif kind == "hover_chart":
                    await self.hover(a[1], a[2])
                    await asyncio.sleep(0.6)
                elif kind == "click":
                    await self.click(a[1])
                elif kind == "select":
                    await self.hover(a[1])
                    await self.page.select_option(a[1], a[2])
                    await asyncio.sleep(0.8)
                elif kind == "scroll":
                    await self.scroll(a[1])
                elif kind == "scroll_px":
                    await self.scroll_to_y(await self.page.evaluate("window.scrollY") + a[1])
                elif kind == "scroll_top":
                    await self.scroll_to_y(0)
            except Exception as e:  # keep recording even if one cue misses
                print(f"   action {a} skipped: {type(e).__name__}", flush=True)


def card_html(kind, s):
    """Animated title card. Lines appear in time with the narration's sentences."""
    words = s.get("words", [])
    lines, t = [], []
    if s["line"]:
        sentences = re.split(r"(?<=[.?!])\s+", s["line"])
        idx = 0
        for sent in sentences:
            n = len(sent.split())
            start = words[min(idx, len(words) - 1)][0] + LEAD_IN if words else 0
            lines.append(sent)
            t.append(start)
            idx += n
    style = """
    body{margin:0;width:100vw;height:100vh;overflow:hidden;font-family:Inter,'Avenir Next',Helvetica,sans-serif;color:#fff;
      background:radial-gradient(1200px 700px at 70% 20%,#312e81 0,#0b1022 60%,#05070f 100%);display:flex;align-items:center;justify-content:center}
    .stars i{position:absolute;width:2px;height:2px;background:#c7d2fe;border-radius:50%;opacity:.0;animation:tw 4s infinite}
    @keyframes tw{0%,100%{opacity:.15}50%{opacity:.9}}
    .wrap{position:relative;width:1300px;text-align:center}
    .logo{width:120px;height:120px;margin:0 auto 34px;opacity:0;transform:scale(.85);animation:in 1.2s .2s forwards;filter:drop-shadow(0 18px 40px rgba(79,70,229,.6))}
    .ln{font-size:52px;line-height:1.25;font-weight:700;letter-spacing:-.01em;opacity:0;transform:translateY(16px);margin:0 0 18px}
    .ln.show{animation:in .9s forwards}
    .ln.dim{color:#a5b4fc;font-weight:600;font-size:40px}
    .moon{color:#fbbf24}
    .brand{margin-top:38px;font-size:30px;font-weight:600;opacity:0;animation:in 1s forwards}
    .brand b{background:linear-gradient(90deg,#fde68a,#f59e0b);-webkit-background-clip:text;color:transparent}
    .meta{font-size:22px;color:#94a3b8;margin-top:12px;opacity:0;animation:in 1s forwards}
    .chapter{font-size:76px;font-weight:800;letter-spacing:-.02em;opacity:0;animation:inout 2.6s forwards}
    .eyebrow{font-size:20px;letter-spacing:.3em;color:#fbbf24;font-weight:700;opacity:0;animation:inout 2.6s forwards;margin-bottom:18px}
    @keyframes in{to{opacity:1;transform:none}}
    @keyframes inout{0%{opacity:0;transform:translateY(14px)}22%,78%{opacity:1;transform:none}100%{opacity:0;transform:translateY(-8px)}}
    """
    stars = "".join(f'<i style="left:{(i * 137) % 100}%;top:{(i * 61) % 100}%;animation-delay:{(i % 7) * .55}s"></i>' for i in range(70))
    logo = f'<div class="logo">{LOGO_SVG.replace("<svg ", "<svg width=\'120\' height=\'120\' ")}</div>'
    if kind == "chapter":
        body = f'<div class="wrap"><div class="eyebrow">NIGHTTWIN</div><div class="chapter">{s["scene"][1]}</div></div>'
    else:
        items = []
        for i, (ln, st) in enumerate(zip(lines, t)):
            cls = "ln dim" if (kind == "intro" and i < len(lines) - 1) or (kind == "outro" and i < 2) else "ln"
            items.append(f'<p class="{cls}" style="animation-delay:{st:.2f}s">{ln}</p>')
        end = (t[-1] + 2.5) if t else 1
        meta = ("Team TwinPulse · Newton School of Technology, Rishihood University" if kind == "outro"
                else "Happiest Health Digital Twin Challenge 2026 · Team TwinPulse")
        body = (f'<div class="wrap">{logo}{"".join(items)}'
                f'<div class="brand" style="animation-delay:{end:.2f}s">Night<b>Twin</b></div>'
                f'<div class="meta" style="animation-delay:{end + .4:.2f}s">{meta}</div></div>')
        body = body.replace('class="ln', 'class="ln show', len(items)).replace("show show", "show")
    return f"<!doctype html><html><head><meta charset='utf-8'><link href='https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800&display=swap' rel='stylesheet'><style>{style}</style></head><body><div class='stars'>{stars}</div>{body}</body></html>"


async def record_all(segs):
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True, args=["--hide-scrollbars", "--force-color-profile=srgb"])
        ctx = await browser.new_context(viewport={"width": int(W / 1.2), "height": int(H / 1.2)}, device_scale_factor=1.2)
        await ctx.add_init_script(CURSOR_JS)
        page = await ctx.new_page()
        await page.goto(f"{APP}/#overview", wait_until="networkidle")
        await asyncio.sleep(1.0)
        session = await ctx.new_cdp_session(page)
        rec = Recorder(page, session)
        await rec.start()
        for i, s in enumerate(segs):
            kind = s["scene"][0]
            if kind not in ("demo", "card", "chapter"):
                continue
            target = s["target"]
            if kind in ("card", "chapter"):
                cpage = await ctx.new_page()
                csess = await ctx.new_cdp_session(cpage)
                crec = Recorder(cpage, csess)
                html = os.path.join(WORK, f"card_{i}.html")
                with open(html, "w") as f:
                    f.write(card_html("chapter" if kind == "chapter" else s["scene"][1], s))
                await cpage.goto("file://" + html, wait_until="load")
                await crec.start()
                t0 = time.time()
                await asyncio.sleep(target)
                s["window"] = (t0, time.time())
                await csess.send("Page.stopScreencast")
                s["frames"] = crec.frames
                await cpage.close()
            else:
                await page.bring_to_front()
                await asyncio.sleep(0.3)
                t0 = time.time()
                await rec.run(s["scene"][1])
                left = target - (time.time() - t0)
                if left > 0:
                    await asyncio.sleep(left)
                s["window"] = (t0, time.time())
                s["frames"] = rec.frames
                if "github.com" in page.url:
                    await page.goto(f"{APP}/#overview", wait_until="networkidle")
            print(f"recorded {i + 1}/{len(segs)} {kind} {s['window'][1] - s['window'][0]:.1f}s", flush=True)
        await browser.close()


def frames_to_clip(s, out):
    t0, t1 = s["window"]
    frames = sorted(s["frames"], key=lambda f: f[0])
    before = [f for f in frames if f[0] <= t0]
    inside = [f for f in frames if t0 < f[0] < t1]
    seq = ([(t0, before[-1][1])] if before else []) + inside
    if not seq:
        seq = [(t0, frames[-1][1])] if frames else []
    d = out + "_frames"
    os.makedirs(d, exist_ok=True)
    lst = []
    for k, (ts, jpg) in enumerate(seq):
        path = os.path.join(d, f"{k:05d}.jpg")
        with open(path, "wb") as f:
            f.write(jpg)
        nxt = seq[k + 1][0] if k + 1 < len(seq) else t1
        lst.append(f"file '{path}'\nduration {max(nxt - ts, 0.001):.4f}\n")
    lst.append(f"file '{os.path.join(d, f'{len(seq) - 1:05d}.jpg')}'\n")
    with open(out + ".txt", "w") as f:
        f.writelines(lst)
    dur = t1 - t0
    sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", out + ".txt", "-vf",
        f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p",
        "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", out])
    shutil.rmtree(d, ignore_errors=True)
    return dur


# ---------------------------------------------------------------- 4. slides
def slide_clip(png, dur, out, k):
    n = max(1, int(round(dur * FPS)))
    zin = k % 2 == 0  # alternate gentle push-in / pull-out
    z = f"if(eq(on,0),1.0,min(zoom+{0.06 / n:.6f},1.06))" if zin else f"if(eq(on,0),1.06,max(zoom-{0.06 / n:.6f},1.0))"
    sh(["ffmpeg", "-y", "-loop", "1", "-i", png, "-vf",
        f"scale={W * 2}:{H * 2},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},format=yuv420p",
        "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-an", out])
    return n / FPS


# ---------------------------------------------------------------- 5. captions, audio, music
def font(size):
    for path, idx in [("/System/Library/Fonts/Avenir Next.ttc", 2), ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0)]:
        try:
            return ImageFont.truetype(path, size, index=idx)
        except Exception:
            continue
    return ImageFont.load_default()


def caption_png(text, path, fnt):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=fnt) > 1350 and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = trial
    lines.append(cur)
    lh = fnt.size + 12
    bw = max(d.textlength(l_, font=fnt) for l_ in lines) + 56
    bh = lh * len(lines) + 30
    x0, y0 = (W - bw) / 2, H - 46 - bh
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=16, fill=(8, 11, 25, 190))
    for i, l_ in enumerate(lines):
        d.text(((W - d.textlength(l_, font=fnt)) / 2, y0 + 15 + i * lh), l_, font=fnt, fill=(255, 255, 255, 255))
    img.save(path)


def caption_chunks(s):
    """Caption lines from the script's own text (keeps punctuation), timed against the voice's word positions."""
    words = s.get("words", [])
    toks = s["line"].split()
    if not words or not toks:
        return []
    chunks, cur = [], []
    for tk in toks:
        cur.append(tk)
        if len(cur) >= 9 or (len(cur) >= 4 and re.search(r"[.?!,;:]$", tk)):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    out, done = [], 0
    for c in chunks:
        i0 = min(int(done / len(toks) * len(words)), len(words) - 1)
        done += len(c)
        i1 = min(max(int(done / len(toks) * len(words)) - 1, i0), len(words) - 1)
        out.append((words[i0][0], words[i1][0] + words[i1][1], " ".join(c)))
    return out


def main():
    for tool in ("ffmpeg", "ffprobe", "pdftoppm"):
        if not shutil.which(tool):
            sys.exit(f"missing {tool}")
    os.makedirs(os.path.join(WORK, "voice"), exist_ok=True)
    clips = os.path.join(WORK, "clips")
    shutil.rmtree(clips, ignore_errors=True)
    os.makedirs(clips)
    segs = [dict(s) for s in SCRIPT]
    if os.environ.get("ONLY"):  # e.g. ONLY=0:8 renders a slice for a quick check
        a, b = map(int, os.environ["ONLY"].split(":"))
        segs = segs[a:b]

    asyncio.run(make_voices(segs))
    for s in segs:
        s["target"] = (LEAD_IN + s["audio"] + TAIL) if s["line"] else CHAPTER_SECONDS

    slides_dir = os.path.join(WORK, "slides")
    os.makedirs(slides_dir, exist_ok=True)
    sh(["pdftoppm", "-png", "-scale-to-x", str(W), "-scale-to-y", str(H),
        os.path.join(ROOT, "docs", "TwinPulse_Presentation.pdf"), os.path.join(slides_dir, "slide")])

    asyncio.run(record_all(segs))

    # video clips
    prev_kind = None
    for i, s in enumerate(segs):
        out = os.path.join(clips, f"{i:03d}.mp4")
        kind = s["scene"][0]
        if kind == "slide":
            s["dur"] = slide_clip(os.path.join(slides_dir, f"slide-{s['scene'][1]:02d}.png"), s["target"], out, i)
        else:
            s["dur"] = frames_to_clip(s, out)
        # gentle dip-through-dark when the kind of scene changes
        if prev_kind is not None and (kind != prev_kind or kind == "slide" and segs[i - 1]["scene"] != s["scene"]):
            faded = out.replace(".mp4", "_f.mp4")
            sh(["ffmpeg", "-y", "-i", out, "-vf", "fade=t=in:st=0:d=0.35", "-c:v", "libx264", "-preset", "medium", "-crf", "18", faded])
            os.replace(faded, out)
        prev_kind = kind
        print(f"clip {i + 1}/{len(segs)} {kind} {s['dur']:.1f}s", flush=True)

    with open(os.path.join(clips, "list.txt"), "w") as f:
        f.writelines(f"file '{os.path.join(clips, f'{i:03d}.mp4')}'\n" for i in range(len(segs)))
    video = os.path.join(WORK, "video.mp4")
    sh(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(clips, "list.txt"), "-c", "copy", video])

    # narration track: each line placed at its segment start + lead-in
    starts, t = [], 0.0
    for s in segs:
        starts.append(t)
        t += s["dur"]
    total = t
    inputs, filters = [], []
    for k, (s, st) in enumerate([(s, st) for s, st in zip(segs, starts) if s["line"]]):
        inputs += ["-i", s["mp3"]]
        filters.append(f"[{k}:a]aresample=48000,adelay={int((st + LEAD_IN) * 1000)}:all=1[a{k}]")
    n = len(filters)
    mix = ";".join(filters) + ";" + "".join(f"[a{k}]" for k in range(n)) + f"amix=inputs={n}:normalize=0:dropout_transition=0,apad=whole_dur={total:.3f}[voice]"
    voice = os.path.join(WORK, "voice.wav")
    sh(["ffmpeg", "-y", *inputs, "-filter_complex", mix, "-map", "[voice]", "-ac", "2", "-ar", "48000", "-t", f"{total:.3f}", voice])

    # soft music bed under the opening and closing cards
    music = os.path.join(WORK, "music.wav")
    bed = []
    for s, st in zip(segs, starts):
        if s["scene"][0] == "card":
            bed.append((st, s["dur"]))
    expr = "0.5*sin(2*PI*220*t)+0.35*sin(2*PI*261.63*t)+0.3*sin(2*PI*329.63*t)+0.2*sin(2*PI*110*t)"
    vol = "+".join(f"between(t,{a:.2f},{a + d:.2f})*min(1,min((t-{a:.2f})/1.5,({a + d:.2f}-t)/2.0))" for a, d in bed) or "0"
    sh(["ffmpeg", "-y", "-f", "lavfi", "-i", f"aevalsrc='{expr}':s=48000:d={total:.3f}", "-af",
        f"lowpass=f=900,tremolo=f=0.15:d=0.5,volume='0.045*({vol})':eval=frame,aformat=channel_layouts=stereo", music])

    # captions
    fnt = font(34)
    capdir = os.path.join(WORK, "captions")
    shutil.rmtree(capdir, ignore_errors=True)
    os.makedirs(capdir)
    blank = os.path.join(capdir, "blank.png")
    Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
    events = []
    for s, st in zip(segs, starts):
        if s["scene"][0] == "card":
            continue  # the card itself shows the words
        for a, b, text in caption_chunks(s):
            events.append((st + LEAD_IN + a, st + LEAD_IN + b + 0.15, text))
    lst, cursor = [], 0.0
    for k, (a, b, text) in enumerate(events):
        if a > cursor:
            lst.append(f"file '{blank}'\nduration {a - cursor:.3f}\n")
        png = os.path.join(capdir, f"c{k:04d}.png")
        caption_png(text, png, fnt)
        end = min(b, events[k + 1][0]) if k + 1 < len(events) else b
        lst.append(f"file '{png}'\nduration {max(end - max(a, cursor), 0.05):.3f}\n")
        cursor = max(end, cursor)
    lst.append(f"file '{blank}'\nduration {max(total - cursor, 0.1):.3f}\nfile '{blank}'\n")
    with open(os.path.join(capdir, "list.txt"), "w") as f:
        f.writelines(lst)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sh(["ffmpeg", "-y", "-i", video, "-f", "concat", "-safe", "0", "-i", os.path.join(capdir, "list.txt"), "-i", voice, "-i", music,
        "-filter_complex",
        f"[1:v]format=rgba,fps={FPS}[cap];[0:v][cap]overlay=0:0:shortest=0:eof_action=pass,fade=t=in:st=0:d=0.8,fade=t=out:st={total - 1.2:.2f}:d=1.2,format=yuv420p[v];"
        f"[2:a][3:a]amix=inputs=2:normalize=0,afade=t=out:st={total - 1.5:.2f}:d=1.5[a]",
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k",
        "-t", f"{total:.3f}", "-movflags", "+faststart", OUT])
    print(f"{OUT}  {total / 60:.1f} min")


if __name__ == "__main__":
    main()
