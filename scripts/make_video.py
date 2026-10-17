"""Build the narrated walkthrough video (docs/video/NightTwin_Walkthrough.mp4, about 22 minutes).

Needs: macOS `say` (voices Tara and Aman, English India), ffmpeg, pdftoppm, Google Chrome,
and the app running on http://localhost:8000 (./run.sh). Slides come from docs/TwinPulse_Presentation.pdf.
The narration text below is also the team's script if you record with your own voices.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "video", "NightTwin_Walkthrough.mp4")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
APP = os.environ.get("APP_URL", "http://localhost:8000")
VOICES = {"A": "Aman", "R": "Rishi"}  # Manan -> Aman, Manas -> Rishi (English, India)
RATE = "145"
TEMPO = 0.93  # macOS voices read fast; slow them a little (pitch preserved)

# Dashboard frames: (name, route, y-offset of the 1080-px crop in a 1920-px-wide capture)
FRAMES = {
    "overview_top": ("overview", 0), "overview_proof": ("overview", 950), "board": ("board", 0),
    "ananya_top": ("patient/TP-001", 0), "ananya_record": ("patient/TP-001", 740),
    "ananya_plan": ("patient/TP-001?snack=15&shift=90&approve=1", 1000), "ananya_snack": ("patient/TP-001?snack=15", 880),
    "ananya_timeline": ("patient/TP-001", 1880), "arjun_top": ("patient/TP-002", 0), "arjun_guard": ("patient/TP-002", 1300),
    "sensors": ("sensors", 0), "evidence_top": ("evidence", 0), "evidence_honest": ("evidence", 900), "privacy": ("about", 0),
}

# Narration comes from scripts/video_script.py (the same script the team records from).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from video_script import S as SCRIPT  # noqa: E402

SPEAKER_VOICE = {"Manan": "A", "Manas": "R"}
SAY = [  # how the synthetic voices should pronounce abbreviations
    (r"\bCGMs\b", "C G Ms"), (r"\bCGM\b", "C G M"), (r"\bNPH\b", "N P H"), (r"\bFHIR R4\b", "F H I R R 4"),
    (r"\bFHIR\b", "F H I R"), (r"\bHbA1c\b", "H b A 1 c"), (r"\bHLA\b", "H L A"), (r"\bDCCT\b", "D C C T"),
    (r"\bIDF\b", "I D F"), (r"\bDPDP\b", "D P D P"), (r"\bCDSCO\b", "C D S C O"), (r"\bABHA\b", "A B H A"),
    (r"\bNGO\b", "N G O"), (r"\bFastAPI\b", "Fast A P I"), (r"\bAPI\b", "A P I"), (r"\bLightGBM\b", "Light G B M"),
    (r"HUPA-UCM", "H U P A U C M"), (r"T1D-UOM", "T 1 D U O M"), (r"\bnumba\b", "numba"), (r"\bPM\b", "P M"),
    (r"\bUK\b", "U K"), (r"\bNASA\b", "NASA"), (r"thirty-seventy", "thirty seventy"),
]
SCENES = []
for seg in SCRIPT:
    text = seg["line"]
    for pat, rep in SAY:
        text = re.sub(pat, rep, text)
    SCENES.append((seg["img"], SPEAKER_VOICE[seg["who"]], text))


def run(cmd, **kw):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)


def capture_frames(tmp):
    raw = {}
    for name, (route, y) in FRAMES.items():
        if route not in raw:
            path = os.path.join(tmp, f"raw_{len(raw)}.png")
            run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1280,3200",
                 "--force-device-scale-factor=1.5", "--virtual-time-budget=12000", f"--screenshot={path}", f"{APP}/#{route}"])
            raw[route] = path
        im = Image.open(raw[route]).convert("RGB")
        im.crop((0, y, 1920, y + 1080)).save(os.path.join(tmp, f"{name}.png"))


def main():
    for tool in ("say", "ffmpeg", "pdftoppm"):
        if not shutil.which(tool):
            sys.exit(f"missing {tool}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="nighttwin_video_")
    run(["pdftoppm", "-png", "-scale-to-x", "1920", "-scale-to-y", "1080",
         os.path.join(ROOT, "docs", "TwinPulse_Presentation.pdf"), os.path.join(tmp, "slide")])
    capture_frames(tmp)
    parts = []
    total_words = 0
    for i, (img, voice, text) in enumerate(SCENES):
        total_words += len(text.split())
        aiff = os.path.join(tmp, f"a{i:02d}.aiff")
        run(["say", "-v", VOICES[voice], "-r", RATE, "-o", aiff, text])
        seg = os.path.join(tmp, f"s{i:02d}.mp4")
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", aiff],
                                   capture_output=True, text=True).stdout) / TEMPO + 2.0  # slightly slower speech + pause
        run(["ffmpeg", "-y", "-loop", "1", "-framerate", "25", "-t", f"{dur:.3f}", "-i", os.path.join(tmp, f"{img}.png"),
             "-i", aiff, "-af", f"atempo={TEMPO},apad", "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
             "-pix_fmt", "yuv420p", "-r", "25", "-c:a", "aac", "-b:a", "128k", "-ar", "44100", seg])
        parts.append(seg)
        print(f"scene {i + 1}/{len(SCENES)}", flush=True)
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", OUT])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", OUT],
                         capture_output=True, text=True).stdout.strip()
    print(f"{OUT}  {float(dur) / 60:.1f} min, {total_words} words")


if __name__ == "__main__":
    main()
