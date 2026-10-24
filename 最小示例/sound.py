"""声音层：点缀 + 一段后台循环；再与旁白混成 mix.wav。调用 score-claude 的 synth/kit（不改它们）。"""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "声音"))
import numpy as np
from scipy.io import wavfile
from scipy import signal
from kit import *   # synth + kit

HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, "timeline.json"), encoding="utf-8"))
S = {s["id"]: s for s in TL["segments"]}
CS = lambda i, k: S[i]["chunks"][k]["start"]
CE = lambda i, k: S[i]["chunks"][k]["end"]
DUR = TL["duration"]
T_AB = S["S04"]["end"] + 0.45; T_BC = S["S05"]["end"] + 0.30; T_CD = S["S07"]["end"] + 0.30

out = Bus(DUR)
place = make_place(out)
cues = []
def cue(t, what, rel):
    cues.append((round(t, 2), what, rel))

# ---------- 场景 A：平台界面层，中性（柔方波单音）----------
t = 1.25 + 0.0; place(beep(m('A5'), 0.1), t, -6, 0.2, (0.8, 0.12)); cue(t, "已受理 chip 出现：单音", -6)
t0 = CS("S02", 2) + 0.15
for i in range(8):                                   # 排位数字滚动：一串小音，音高上行
    place(tick(0.05, 2200 + 180 * i), t0 + i * 0.27, -13, 0.2, (0.5, 0.1))
cue(t0, "排位数字滚动：8 个 tick 上行", -13)
t = CS("S03", 0) + 0.5; place(click(), t, -7, -0.2, (0.6, 0.1)); cue(t, "预计处理时间开始打字：点击", -7)
t = CS("S04", 0) + 1.0
place(beep(m('E4'), 0.14), t, -3, 0.0, (0.8, 0.12)); place(beep(m('Bb3'), 0.2), t + 0.16, -3, 0.0, (0.8, 0.12))   # 冷两声（三全音）
cue(t, "7个工作日被划掉：两声冷提示（三全音）", -3)
for i in range(6):                                   # 施工日历：6 格慢串，上行木槌
    place(mallet(m(['C5', 'D5', 'E5', 'F5', 'G5', 'A5'][i]), 0.5), CS("S04", 1) + 0.45 + i * 0.33, -11, -0.4 + 0.15 * i, (1.0, 0.16))
cue(CS("S04", 1) + 0.45, "施工 6 格：慢串木槌（C 大调上行）", -11)
t = CS("S04", 1) + 2.45; place(knock_note(m('D3'), 1.0), t, -4, 0.0, (1.0, 0.15)); cue(t, "第七天休息：低沉木敲", -4)
t = CS("S04", 2) + 0.15; place(pluck(m('B5'), 1.6), t, -6, 0.3, (1.6, 0.25)); cue(t, "第八天，无名：一个悬着的单音（B，不解决）", -6)

# ---------- 场景 B：后台循环（D 小调，100 BPM）----------
BPM = 100; B1 = 60 / BPM; BAR = 4 * B1
L = Bus(DUR)
prog = [(['D3', 'F3', 'A3', 'C4'], 'D2'), (['Bb2', 'D3', 'F3', 'A3'], 'Bb1'), (['G2', 'Bb2', 'D3', 'F3'], 'G1'), (['A2', 'C#3', 'E3', 'G3'], 'A1')]
T0 = CS("S05", 0) - 0.05; STOP_B = S["S05"]["end"] + 0.1
k = 0
while T0 + k * BAR < STOP_B + BAR:
    v, root = prog[k % 4]; t = T0 + k * BAR
    for q in range(8):   # 八分音符琶音，固定音型
        nm = v[[0, 2, 1, 3, 2, 1, 3, 2][q]]
        L.add(pluck(m(nm) + 12, 0.45, 0.4), t + q * B1 / 2, 0.075, pan=-0.3 + 0.08 * q)
    L.add(bass(m(root) + 12, 1.2 * B1), t, 0.10); L.add(bass(m(root) + 12, 0.8 * B1), t + 2.5 * B1, 0.07)
    for q in range(4): L.add(hat(), t + q * B1 + 0.5 * B1, 0.07, 0.25)
    k += 1
l = reverb(L.x, 1.2, 0.18)
l = tapestop(l, STOP_B, 0.5)
l = level_bus(l, T0 + 2, STOP_B - 1, -6)
# 循环让路：重拍前后压 7 dB
t_merge = CS("S05", 1) + 2.0; t_fmt = CS("S05", 2) + 2.1; t_cut = CS("S05", 3) + 1.95
tt = np.arange(l.shape[1]) / SR; g = np.ones_like(tt); d = 10 ** (-7 / 20)
for a_ in (t_merge, t_fmt, t_cut):
    g = np.minimum(g, np.interp(tt, [a_ - 0.15, a_, a_ + 0.9, a_ + 1.3], [1, d, d, 1], left=1, right=1))
out.x += l * g
cue(T0, "后台循环起（D 小调琶音，100BPM）；三处重拍压低 7dB 让路", -6)
cue(STOP_B, "循环 tapestop 切断（场景 B 结束）", 0)
place(stamp([m('D4'), m('Ab4')]), t_merge, -2, 0.0, (1.2, 0.2)); cue(t_merge, "祈祷合并为一：闷击", -2)
place(beep(m('F4'), 0.12), t_fmt, -3, 0.0, (0.8, 0.1)); place(beep(m('B3'), 0.22), t_fmt + 0.16, -3, 0.0, (0.8, 0.1)); cue(t_fmt, "格式不受支持：两声冷提示", -3)
place(crunch(0.25) + 0.6 * knock_note(m('A2'), 0.5)[:int(0.25 * SR)], t_cut, -2, 0.0, (0.8, 0.12)); cue(t_cut, "诗被截断：断裂声", -2)

# ---------- 场景 C：刷新 ----------
refT = CS("S06", 0)
t = refT; n = 0
goT = CS("S07", 0) + 1.15; backT = CS("S07", 1) + 1.55
while t < goT - 0.5:
    place(tick(0.04, 2600), t, -11, 0.3, (0.5, 0.08)); t += 1.6; n += 1
cue(refT, f"自动刷新：每 1.6 秒一个轻 tick（{n} 次）", -11)
t = CS("S06", 2) + 1.1; place(beep(m('C6'), 0.1), t, -6, 0.2, (0.8, 0.12)); cue(t, "“稳定”标记：单音", -6)
place(gliss(m('D5'), m('D6'), 1.3), goT, -5, 0.0, (1.5, 0.25)); cue(goT, "排位前进一位：玻璃音上滑", -5)
place(gliss(m('A5'), m('A4'), 0.5), backT - 0.05, -3, 0.0, (0.8, 0.12)); place(stamp([m('D4'), m('Ab4')]), backT + 0.1, -3, 0.0, (1.0, 0.18)); cue(backT, "显示错误：下滑 + 闷击", -3)

# ---------- 场景 D ----------
t = CS("S08", 0) + 0.8; place(beep(m('E5'), 0.1), t, -5, 0.3, (0.8, 0.12)); place(beep(m('A5'), 0.14), t + 0.14, -5, 0.3, (0.8, 0.12)); cue(t, "新邮件：两音", -5)
r0 = CS("S09", 0)
for i in range(10):
    place(click(), r0 + 0.1 + i * 0.1, -14, -0.2 + 0.04 * i, (0.4, 0.06))
cue(r0 + 0.1, "回复打字：10 下轻点击", -14)
t = r0 + 1.9; place(click(), t, -7, 0.3, (0.6, 0.1)); cue(t, "点击发送", -7)
t = r0 + 2.7; place(church_bell(m('D3'), 5.0), t, -2, 0.0, (2.0, 0.3)); cue(t, "自动回复出现：全片唯一一口钟，之后静默", -2)

# ---------- 总淡出 ----------
x = out.x[:, :int(DUR * SR)]
tt2 = np.arange(x.shape[1]) / SR
x = x * np.clip((DUR - tt2) / 1.0, 0, 1)

print("music peak", np.abs(x).max())
wavfile.write(os.path.join(HERE, "music.wav"), SR, x.T.astype(np.float32))
with open(os.path.join(HERE, "cues.md"), "w", encoding="utf-8", newline="") as f:
    f.write("| 时间 | 画面/声音 | rel |\n|---|---|---|\n")
    for c in sorted(cues): f.write(f"| {c[0]} | {c[1]} | {c[2]} |\n")

# ---------- 与旁白混合（逻辑同 mix_sample.py，旁白改为本目录 voice.wav）----------
if not os.path.exists(os.path.join(HERE, "voice.wav")):
    sys.exit("没有 voice.wav（旁白需先用 TTS 生成并跑 build_voice.py），只输出了 music.wav")
def movavg(a, w):
    c = np.concatenate([[0.0], np.cumsum(a)]); e = (c[w:] - c[:-w]) / w
    o = np.empty_like(a); h = w // 2; o[:h] = e[0]; o[h:h + len(e)] = e; o[h + len(e):] = e[-1]; return o
_, v = wavfile.read(os.path.join(HERE, "voice.wav")); v = v.astype(np.float64) / 32768
mu = x.copy(); n = min(len(v), mu.shape[1]); v = v[:n]; mu = mu[:, :n]
act = 20 * np.log10(np.sqrt(movavg(v ** 2, int(0.05 * SR))) + 1e-9) > -45
act = movavg(act.astype(float), int(0.5 * SR)) > 0
b, a = signal.butter(4, 300 / (SR / 2), 'high')
pv = movavg(signal.lfilter(b, a, v) ** 2, int(0.4 * SR))
vref = 10 * np.log10(np.percentile(pv[act], 90) + 1e-12)
gain = 10 ** ((vref - 2 - REF) / 20)
mix = np.vstack([v, v]) + mu * gain
pk = np.abs(mix).max()
if pk > 0.89: mix *= 0.89 / pk
print("voice phone p90", round(vref, 1), "music gain dB", round(20 * np.log10(gain), 1), "peak", round(pk, 3), "sound peaks/s>1.6*:", [i for i, p in enumerate(peaks_per_second(x)) if p > 1.6])
wavfile.write(os.path.join(HERE, "mix.wav"), SR, mix.T.astype(np.float32))
