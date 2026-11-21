#!/usr/bin/env python3
"""Generates the test patterns shipped in usr/share/strawberry-video-player/patterns/.

  python3 tools/make-patterns.py OUTDIR

Needs python3-pil. The audio/sync clip also needs ffmpeg (libx264, aac).
Stills are 1920x1080 PNGs; the audio/sync clip is a 30 second 960x540 30p H.264 file (heavily compressed).
"""
import math
import os
import struct
import subprocess
import sys
import tempfile
import wave

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
WHITE, BLACK, RED, GREY = (255, 255, 255), (0, 0, 0), (250, 32, 33), (126, 126, 126)


def font(size):
    return ImageFont.load_default(size=size)


def colour_bars():
    im = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(im)
    bars = [(191, 191, 191), (191, 191, 0), (0, 191, 191), (0, 191, 0),
            (191, 0, 191), (191, 0, 0), (0, 0, 191), (0, 0, 0)]
    bw = W // 8
    top = int(H * 0.72)
    for i, c in enumerate(bars):
        d.rectangle([i * bw, 0, (i + 1) * bw - 1, top], fill=c)
    # lower strip: 11 grey steps, 0..100 %
    steps = 11
    sw = W / steps
    for i in range(steps):
        v = round(255 * i / (steps - 1))
        d.rectangle([round(i * sw), top + 1, round((i + 1) * sw) - 1, H - 1], fill=(v, v, v))
    return im


def grey_ramp():
    im = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(im)
    vals = list(range(0, 241, 16)) + [255]          # 0,16,...,240,255
    bw = 112
    x0 = (W - bw * len(vals)) // 2
    d.text((W // 2, 90), "GREY STEPS: every block should be distinct", fill=WHITE,
           font=font(44), anchor="mm")
    for i, v in enumerate(vals):
        x = x0 + i * bw
        d.rectangle([x, 200, x + bw - 1, 620], fill=(v, v, v))
        d.text((x + bw // 2, 660), str(v), fill=WHITE, font=font(34), anchor="mm")
    d.text((W // 2, 760), "0 and 16 look the same: blacks are crushed.   235, 240 and 255 look the same: whites are clipped.",
           fill=GREY, font=font(30), anchor="mm")
    for x in range(x0, x0 + bw * len(vals)):                   # smooth ramp
        v = round(255 * (x - x0) / (bw * len(vals) - 1))
        d.line([(x, 840), (x, 980)], fill=(v, v, v))
    return im


def geometry():
    im = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(im)
    for x in range(0, W + 1, 120):
        d.line([(x, 0), (x, H)], fill=(50, 50, 50), width=1)
    for y in range(0, H + 1, 120):
        d.line([(0, y), (W, y)], fill=(50, 50, 50), width=1)
    d.rectangle([0, 0, W - 1, H - 1], outline=WHITE, width=6)
    s = 540
    d.rectangle([300, 270, 300 + s - 1, 270 + s - 1], outline=WHITE, width=10)
    d.ellipse([1080, 270, 1080 + s - 1, 270 + s - 1], outline=WHITE, width=10)
    d.line([(300, 270), (300 + s, 270 + s)], fill=RED, width=4)
    d.line([(300 + s, 270), (300, 270 + s)], fill=RED, width=4)
    d.line([(1080, 270 + s // 2), (1080 + s, 270 + s // 2)], fill=RED, width=4)
    d.line([(1080 + s // 2, 270), (1080 + s // 2, 270 + s)], fill=RED, width=4)
    d.text((570, 225), "1:1 SQUARE", fill=WHITE, font=font(44), anchor="mm")
    d.text((1350, 225), "CIRCLE", fill=WHITE, font=font(44), anchor="mm")
    d.text((W // 2, 880), "The square must be square and the circle round.", fill=WHITE,
           font=font(34), anchor="mm")
    d.text((W // 2, 935), "If they look tall or wide, press 1-8 to set the display's aspect ratio.",
           fill=GREY, font=font(30), anchor="mm")
    return im


def convergence():
    """White grid inside a red ring of cells, a dot in the middle of every cell."""
    im = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(im)
    cell = 60
    cols, rows = W // cell, H // cell
    for c in range(cols + 1):                                   # red grid everywhere
        x = min(c * cell, W - 1)
        d.line([(x, 0), (x, H)], fill=RED, width=4)
    for r in range(rows + 1):
        y = min(r * cell, H - 1)
        d.line([(0, y), (W, y)], fill=RED, width=4)
    x0, y0, x1, y1 = cell, cell, W - cell, H - cell             # white grid inside
    for c in range(1, cols):
        d.line([(c * cell, y0), (c * cell, y1)], fill=WHITE, width=4)
    for r in range(1, rows):
        d.line([(x0, r * cell), (x1, r * cell)], fill=WHITE, width=4)
    for c in range(cols):
        for r in range(rows):
            cx, cy = c * cell + cell // 2, r * cell + cell // 2
            inner = 1 <= c < cols - 1 and 1 <= r < rows - 1
            d.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=WHITE if inner else RED)
    return im


def sync_frame(kind):
    """kind: idle | left | right | both"""
    im = Image.new("RGB", (W, H), (16, 16, 16))
    d = ImageDraw.Draw(im)
    lit = {"left": [(0, 0, W // 2 - 1, H - 1)], "right": [(W // 2, 0, W - 1, H - 1)],
           "both": [(0, 0, W - 1, H - 1)], "idle": []}[kind]
    for box in lit:
        d.rectangle(box, fill=WHITE)
    ink = lambda lit_side: BLACK if lit_side else WHITE
    d.text((W // 4, H // 2), "LEFT", fill=ink(kind in ("left", "both")), font=font(120), anchor="mm")
    d.text((3 * W // 4, H // 2), "RIGHT", fill=ink(kind in ("right", "both")), font=font(120), anchor="mm")
    d.text((W // 2, 120), "AUDIO + SYNC TEST", fill=ink(kind == "both"), font=font(54), anchor="mm")
    d.text((W // 2, H - 100), "A tone (1 kHz) sounds with each flash: left, right, then both.",
           fill=ink(kind == "both"), font=font(32), anchor="mm")
    d.text((W // 2, H - 55), "Picture and sound should land together.",
           fill=ink(kind == "both") if kind == "both" else GREY, font=font(30), anchor="mm")
    return im


def audio_wav(path, rate=48000):
    """5 s: left beep at 0.0, right beep at 1.0, both at 2.0; each 0.4 s, 1 kHz, -12 dBFS."""
    n = 5 * rate
    amp = 0.25 * 32767
    frames = bytearray()
    for i in range(n):
        t = i / rate
        l = r = 0.0
        for start, left, right in ((0.0, True, False), (1.0, False, True), (2.0, True, True)):
            if start <= t < start + 0.4:
                x = t - start
                env = min(1.0, x / 0.01, (0.4 - x) / 0.01)    # 10 ms fades: no clicks
                v = math.sin(2 * math.pi * 1000 * x) * env * amp
                l += v if left else 0
                r += v if right else 0
        frames += struct.pack("<hh", int(l), int(r))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))


def audio_sync_clip(out, seconds=30):
    with tempfile.TemporaryDirectory() as tmp:
        for kind in ("idle", "left", "right", "both"):
            sync_frame(kind).save(os.path.join(tmp, kind + ".png"))
        wav = os.path.join(tmp, "a.wav")
        audio_wav(wav)
        seq = [("left", 0.4), ("idle", 0.6), ("right", 0.4), ("idle", 0.6), ("both", 0.4), ("idle", 2.6)]
        with open(os.path.join(tmp, "list.txt"), "w") as f:
            for kind, dur in seq:
                f.write("file '%s'\nduration %.2f\n" % (os.path.join(tmp, kind + ".png"), dur))
            f.write("file '%s'\n" % os.path.join(tmp, "idle.png"))
        seg = os.path.join(tmp, "seg.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
                        "-i", os.path.join(tmp, "list.txt"), "-i", wav,
                        "-vf", "fps=30,scale=960:540,format=yuv420p",
                        "-c:v", "libx264", "-preset", "ultrafast", "-threads", "1",
                        "-profile:v", "main", "-level", "4.0", "-crf", "40", "-tune", "stillimage", "-g", "150",
                        "-c:a", "aac", "-b:a", "32k", "-ac", "2", "-t", "5", seg], check=True)
        loops = int(seconds / 5) - 1
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", str(loops), "-i", seg,
                        "-c", "copy", "-movflags", "+faststart", out], check=True)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "patterns"
    os.makedirs(out, exist_ok=True)
    for name, fn in (("1-colour-bars", colour_bars), ("2-grey-steps", grey_ramp),
                     ("3-geometry", geometry), ("4-convergence", convergence)):
        fn().save(os.path.join(out, name + ".png"), optimize=True)
        print("wrote", name + ".png")
    audio_sync_clip(os.path.join(out, "5-audio-sync.mp4"))
    print("wrote 5-audio-sync.mp4")


if __name__ == "__main__":
    main()
