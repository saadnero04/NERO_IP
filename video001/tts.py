# Render every line with Kokoro (free, open-source TTS) and write timings.json
import json, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
M = sys.argv[1]
k = Kokoro(M + "/kokoro-v1.0.onnx", M + "/voices-v1.0.bin")
VOICE = {"cashy": ("am_michael", 1.05), "mom": ("af_sarah", 0.92), "boss": ("am_onyx", 0.95), "rosa": ("af_bella", 1.08)}
lines = json.load(open("lines.json"))
SR = 24000
out, t = [], 0.6  # small lead-in
GAP = {"same": 0.25, "new": 0.55}
audio = np.zeros(int(SR * 120), dtype=np.float32)
prev_scene = None
for i, ln in enumerate(lines):
    v, sp = VOICE[ln["speaker"]]
    s, sr = k.create(ln["text"], voice=v, speed=sp, lang="en-us")
    # trim silence
    idx = np.where(np.abs(s) > 0.01)[0]
    s = s[max(0, idx[0] - 600): idx[-1] + 1200]
    if prev_scene is not None:
        t += GAP["same"] if ln["scene"] == prev_scene else GAP["new"]
    start = t; dur = len(s) / SR
    audio[int(start * SR): int(start * SR) + len(s)] += s
    # amplitude envelope for lip sync (per 1/24 s)
    hop = SR // 24
    env = [float(np.sqrt(np.mean(s[j:j + hop] ** 2))) for j in range(0, len(s), hop)]
    out.append({**ln, "start": round(start, 3), "end": round(start + dur, 3), "env": [round(e, 4) for e in env]})
    t = start + dur
    prev_scene = ln["scene"]
total = t + 1.6
audio = audio[: int(total * SR)]
audio = audio / max(1e-6, np.max(np.abs(audio))) * 0.9
sf.write("voice.wav", audio, SR)
json.dump({"total": round(total, 3), "lines": out}, open("timings.json", "w"))
print("total", round(total, 2)); [print(l["speaker"], l["start"], l["end"]) for l in out]
