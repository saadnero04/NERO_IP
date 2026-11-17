# Free original soundtrack + sound effects, synthesized with numpy (no copyright issues)
import json, numpy as np, soundfile as sf
SR = 44100
T = json.load(open("timings.json")); total = T["total"]; lines = T["lines"]
n = int(total * SR); mus = np.zeros(n); sfx = np.zeros(n)
def note(f, start, dur, vol, kind="piano"):
    i0 = int(start * SR); m = min(int(dur * SR), n - i0)
    if m <= 0: return
    t = np.arange(m) / SR
    if kind == "piano":
        w = sum(np.sin(2*np.pi*f*h*t) * a for h, a in [(1, 1), (2, .45), (3, .18), (4, .08)]) * np.exp(-t * 2.6)
        w *= np.minimum(1, t / .005)
    else:  # soft string pad
        w = sum(np.sin(2*np.pi*f*d*t + p) for d, p in [(1, 0), (1.003, 1), (.997, 2)]) / 3
        w += .3 * np.sin(2*np.pi*f*2*t)
        env = np.minimum(1, t / .6) * np.minimum(1, (dur - t) / .6); w *= env
    mus[i0:i0+m] += w * vol
NOTE = lambda s: 440 * 2 ** ((s - 69) / 12)
# scene starts (same rule as scene.html)
scenes = []
for i, l in enumerate(lines):
    if not scenes or scenes[-1][0] != l["scene"]: scenes.append([l["scene"], 0 if i == 0 else l["start"] - .28])
start_of = {s: t for s, t in scenes}
turn = start_of["laptop"]; pay = start_of["payoff"]; cta = start_of["cta"]
# sad section: A minor progression, sparse piano
sad = [(57, [69, 72, 76]), (53, [69, 72, 77]), (48, [67, 72, 76]), (55, [67, 71, 74])]  # Am F C G
beat = 0.75; t = 0.0; k = 0
while t < turn:
    root, ch = sad[(k // 4) % 4]
    if k % 4 == 0: note(NOTE(root - 12), t, 3, .22); note(NOTE(root), t, 3, .12, "pad")
    note(NOTE(ch[k % 3]), t, 1.4, .10)
    t += beat; k += 1
# hopeful section: F C G Am -> brighter, add pulse
hope = [(53, [69, 72, 77]), (48, [67, 72, 76]), (55, [67, 71, 74]), (57, [69, 72, 76])]
t = turn; k = 0
while t < pay:
    root, ch = hope[(k // 4) % 4]
    if k % 4 == 0: note(NOTE(root - 12), t, 2.4, .25); [note(NOTE(c), t, 2.4, .07, "pad") for c in ch]
    note(NOTE(ch[k % 3] + 12), t, .9, .07); note(NOTE(root - 24), t, .3, .10)
    t += 0.5; k += 1
# payoff: warm major crescendo C - G - Am - F, full strings
warm = [(48, [64, 67, 72, 76]), (55, [62, 67, 71, 74]), (57, [64, 69, 72, 76]), (53, [65, 69, 72, 77])]
t = pay; k = 0
while t < total:
    root, ch = warm[k % 4]
    vol = .10 if t < cta else .08
    note(NOTE(root - 12), t, 2.2, .3); [note(NOTE(c), t, 2.2, vol, "pad") for c in ch]
    for j in range(4): note(NOTE(ch[j] + 12), t + j * .5, .8, .06)
    t += 2.0; k += 1
# SFX
def whoosh(at, dur=.35, vol=.35):
    i0 = int(at * SR); m = int(dur * SR); m = min(m, n - i0)
    if m <= 0: return
    noise = np.random.default_rng(int(at * 100)).standard_normal(m)
    k = np.ones(40) / 40; noise = np.convolve(noise, k, 'same')
    env = np.sin(np.linspace(0, np.pi, m)) ** 2
    sfx[i0:i0+m] += noise * env * vol * 3
def thud(at, vol=.9):
    i0 = int(at * SR); m = int(.4 * SR); t = np.arange(m) / SR
    sfx[i0:i0+m] += np.sin(2*np.pi*(90 - 50*t)*t) * np.exp(-t * 9) * vol
def ping(at, f=1760, vol=.25):
    i0 = int(at * SR); m = int(.5 * SR); t = np.arange(m) / SR
    sfx[i0:i0+m] += (np.sin(2*np.pi*f*t) + .5*np.sin(2*np.pi*f*1.5*t)) * np.exp(-t * 7) * vol
for name, st in scenes[1:]: whoosh(max(0, st - .15))
thud(start_of["office"] + .22)
for d in (.5, 1.2, 2.0, 2.7): ping(turn + d, 1568 if d in (.5, 2.0) else 2093, .18)
g = start_of["grind"]; gdur = start_of["payoff"] - g
for j in (1, 2): whoosh(g + j * gdur / 3 - .12, .25, .3)
for j in range(6): ping(g + gdur / 3 + j * .07, 2637, .08)
for j in range(5): ping(pay + .2 + j * .35, 2637 + j * 200, .07)
ping(cta + .1, 1318, .25); ping(cta + .25, 1760, .25)
mus = mus / np.max(np.abs(mus)) * .5
sf.write("music.wav", mus.astype(np.float32), SR); sf.write("sfx.wav", np.clip(sfx, -1, 1).astype(np.float32), SR)
print("ok", round(total, 2))
