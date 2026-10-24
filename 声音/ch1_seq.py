"""第一章 0–123 秒声音层（协调者作曲，r4）。时间＝全片秒＝第一章秒；旁白时间用 outputs/chapter1-r13/data.js（现行），
画面事件来自各镜头 EV 与成片逐帧检测（Approve 按下变暗、bypass 开关变橙、伊甸园灭灯等）。
用户 10/22：「对味了，而且感觉全局光照渲染成功之后的那个旋律重复可以复用一段时间，转折之后再换，加音效就行。」
结构：
  0–26.6  档案段点缀（同 r3 样）
  27–33   “神说，要有光”到“渲染参数”：静默
  33–40.9 光场初始化：玻璃垫音打开、钟音由稀到密（按 r13 时间重排：原样片早了 2.5 秒）
  40.91   “这是宇宙第一次Vibe Coding”：lo-fi 循环起，一直走到“上帝停工”；上面叠创世各步的点缀与每次 Approve 点击
  64.55   “上帝停工”：循环像磁带断电一样停住；之后的 Approve 点击只剩干巴巴的“咔哒”，没有回应
  69.0    “本周使用额度已耗尽”：一声低沉的下行提示
  71.4–84 控制台：多窗口铺开的一串轻响、额度恢复上滑、批准点击、bypass 开关
  84.95   “代理自行执行”：换成第二个循环（自动执行的十六分音符脉冲），无人看管地一直走进伊甸园
  89–98   伊甸园：藤蔓攀上云端的上滑与“已连接”，咬一口果实，循环断开
  100–107 本地蒸馏：上行拨弦越来越密，开成一个暖和弦
  111.9   撤销访问：一切掐断，一声闷击
  113.8   “检测到可疑信号”：两声冷提示
  121.3   “这叫原罪”：一口低沉的教堂钟"""
import os, sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from synth import *

DUR = 124.0
REF = -20.0
out = Bus(DUR)


def phone_level(x, win=0.4):
    y = hp(x.mean(axis=0) if x.ndim == 2 else x, 300, 4)
    w = int(win * SR)
    if len(y) < w: y = np.pad(y, (0, w - len(y)))
    c = np.concatenate([[0], np.cumsum(y ** 2)]); e = (c[w:] - c[:-w]) / w
    return 10 * np.log10(e.max() + 1e-12)


def stereo(sig, pan):
    if sig.ndim == 2: return sig
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    return np.vstack([sig * l * 1.414, sig * r * 1.414])


def place(sig, t, rel=0.0, pan=0.0, verb=(1.6, 0.22)):
    """单个点缀：混响后按手机外放响度归一到 REF+rel。"""
    sig = hp(stereo(sig, pan), 75)
    if verb: sig = reverb(np.hstack([sig, np.zeros((2, int(verb[0] * 1.3 * SR)))]), *verb)
    out.add(sig * 10 ** ((REF + rel - phone_level(sig, 0.1)) / 20), t)   # 短促点缀按 100ms 量（人耳对短声的积分时间），避免点击被过度放大


def level_bus(x, t0, t1, rel):
    seg = x[:, int(t0 * SR):int(t1 * SR)]
    return x * 10 ** ((REF + rel - phone_level(seg)) / 20)


def knock_note(note, dur=1.4):
    n = int(dur * SR); t = np.arange(n) / SR
    y = mallet(note, dur) + 0.5 * mallet(note + 12, dur) * np.exp(-t / 0.3)
    k = int(0.03 * SR)
    y[:k] += bp(rng.uniform(-1, 1, k), 800, 2500) * np.exp(-np.arange(k) / SR / 0.006) * 0.6
    return y


def stamp(tone):
    y = thud(0.7, 90, tone); n = len(y); t = np.arange(n) / SR
    return y + 0.9 * bp(rng.uniform(-1, 1, n), 250, 900) * np.exp(-t / 0.035)


# ================= 0–26.6 档案段（同 r3） =================
place(knock_note(m('D4'), 2.5) + 0.25 * glass(m('D6'), 2.5, 2.0, 0.8), 0.30, -2, verb=(2.4, 0.35))
place(pad([m('D4'), m('A4')], 3.6, a=0.9, r=2.2, cutoff=1400), 1.15, -7, verb=(2.4, 0.4))
place(glass(m('A6'), 1.6, 3.5, 1.2), 2.80, -6, -0.3)
place(paper(0.28), 5.42, -6, -0.2, (0.8, 0.12))
place(stamp([m('D4'), m('F4')]), 6.68, 0, 0.1, (1.8, 0.25))
place(paper(0.35, 900, 4000), 8.95, -6, 0, (0.8, 0.12))
for i in range(4): place(tick(), 9.75 + i * 0.09, -6, -0.15 + 0.1 * i, (0.6, 0.1))
place(mallet(m('A5'), 1.0), 9.75 + 0.33, -5, 0.3)
place(paper(0.4, 800, 3500), 11.89, -6, 0.15, (0.8, 0.12))
place(knock_note(m('D4'), 2.0), 15.95, -5, -0.2, (2.2, 0.35))
place(paper(0.4, 800, 3500), 19.30, -6, -0.1, (0.8, 0.12))
place(mallet(m('D5'), 1.4), 19.55, -3, 0.25); place(mallet(m('F#5'), 1.6), 19.80, -3, 0.3)
place(stamp([m('A3'), m('E4')]), 22.70, 0, -0.1, (1.8, 0.25))
place(paper(0.4, 700, 3000), 23.86, -6, 0, (0.8, 0.12))
place(paper(0.55, 1200, 5000, 0.2), 25.06, -5, 0.2, (0.8, 0.12))
place(pad([m('A3'), m('E4')], 2.0, a=0.7, r=1.2, cutoff=1200), 24.9, -8, verb=(2.4, 0.4))

# ================= 33–40.9 光场初始化（r13 时间） =================
c = Bus(DUR)
c.add(pad([m('D4'), m('F#4'), m('A4'), m('E5')], 10.4, a=6.0, r=2.4, cutoff=500, cutoff_end=3200, detune=9), 33.05, 0.42)
c.add(pad([m('D3'), m('A3')], 9.8, a=6.5, r=2.2, cutoff=400, cutoff_end=1500), 33.5, 0.25)
bells = [33.4, 35.0, 36.0, 36.9, 37.45, 38.0, 38.45, 38.85, 39.25, 39.6, 39.9, 40.2, 40.45, 40.68]
scale = ['A5', 'D6', 'F#5', 'E6', 'A5', 'B5', 'D6', 'F#6', 'E6', 'A6', 'B5', 'D6', 'F#6', 'A6']
for i, (t, nm) in enumerate(zip(bells, scale)):
    c.add(glass(m(nm), 3.2), t, 0.10 + 0.05 * i / len(bells), pan=(-0.5 if i % 2 else 0.5) * 0.6)
out.x += level_bus(reverb(c.x, 3.4, 0.48), 37.4, 40.9, -4)

# ================= 40.91–64.55 Vibe 循环 =================
L1 = Bus(DUR); B2 = 60 / 84; T1 = 40.91; BAR = 4 * B2; STOP = 64.55
prog = [(['D3', 'F#3', 'A3', 'C#4', 'E4'], 'D2'), (['B2', 'D3', 'F#3', 'A3', 'C#4'], 'B1'),
        (['G2', 'B2', 'D3', 'F#3', 'A3'], 'G1'), (['A2', 'D3', 'E3', 'G3', 'B3'], 'A1')]
lick = ['A4', 'F#4', 'E4', 'D4']   # 每两小节一次的小尾巴，让循环有记忆点
k = 0
while T1 + k * BAR < STOP + BAR:
    v, root = prog[k % 4]; t = T1 + k * BAR
    for j, nm in enumerate(v): L1.add(ep(m(nm), BAR * 0.95), t + 0.012 * j, 0.075, pan=-0.3 + 0.15 * j)
    if k % 2 == 1:
        for q, nm in enumerate(lick): L1.add(ep(m(nm) + 12, 0.5), t + (2.5 + 0.5 * q) * B2, 0.045, 0.35)
    L1.add(bass(m(root) + 12, 1.4 * B2), t, 0.11); L1.add(bass(m(root) + 12, 0.9 * B2), t + 2.5 * B2, 0.08)
    for q in range(8):
        L1.add(hat(), t + (q // 2) * B2 + (0.58 * B2 if q % 2 else 0), 0.10 if q % 2 else 0.14, 0.25)
    L1.add(kick(), t, 0.3); L1.add(kick(), t + 2.5 * B2, 0.24)
    L1.add(snare(), t + B2, 0.16, -0.1); L1.add(snare(), t + 3 * B2, 0.16, -0.1)
    k += 1
l1 = reverb(L1.x, 1.4, 0.2)
l1 = tapestop(l1, STOP, 0.45)                     # “上帝停工”：断电
l1 = level_bus(l1, 42, 50, -5)
# 10/22 用户「音效和音乐打架」：植被、星星、复制人这三串小音响时循环让路 7 dB（一个动作只由一层讲），事后 0.4 秒回来
_tt = np.arange(l1.shape[1]) / SR; _g = np.ones_like(_tt); _d = 10 ** (-7 / 20)
for a, b in [(45.10, 45.75), (49.40, 49.80), (52.15, 53.10)]:
    _g = np.minimum(_g, np.interp(_tt, [a - 0.08, a, b, b + 0.4], [1, _d, _d, 1], left=1, right=1))
out.x += l1 * _g

# 创世各步（第三天 42.64 起、第四/六天 47.0 起的镜头 EV）
G3 = 42.64
place(pad([m('D3'), m('A3')], 1.6, a=0.6, r=0.8, cutoff=900), G3 + 1.20, -9)                    # terrain 地形隆起：一口低气
for i in range(12):                                                                           # batch 植被批量生成：一串上行小木槌
    place(mallet(m(['D5', 'E5', 'F#5', 'A5', 'B5', 'D6'][i % 6]) + (12 if i >= 6 else 0), 0.5), G3 + 2.507 + i * 0.05, -11, -0.6 + 0.1 * i, (1.2, 0.2))
place(glass(m('A6'), 1.5), G3 + 3.85, -8, 0.3)                                                # grown 长成
D4 = 47.0
place(toggle(), D4 + 1.18, -6, -0.3, (0.8, 0.12))                                             # hook 日月挂上轨道：咔
place(tick(0.05, 2400), D4 + 2.20, -6, 0.2, (0.6, 0.1)); place(tick(0.05, 1900), D4 + 2.70, -7, 0.2, (0.6, 0.1))   # cron：嘀、嗒
for i, nm in enumerate(['F#6', 'A6', 'D7']): place(glass(m(nm), 1.4), D4 + 2.45 + 0.12 * i, -10, 0.4 - 0.2 * i)     # stars
place(pluck(m('D4'), 1.2, 0.6), D4 + 4.87, -6, 0)                                             # human 人类派生
for i in range(8): place(pluck(m(['A4', 'D5', 'F#5', 'A5'][i % 4]), 0.8, 0.5), D4 + 5.19 + i * 0.12, -10, -0.7 + 0.2 * i, (1.0, 0.15))   # fork 一排排复制出来
place(knock_note(m('A4'), 1.0), D4 + 6.53, -8, 0.2)                                           # memory
place(tick(), D4 + 7.97, -8, -0.2, (0.6, 0.1)); place(tick(), D4 + 8.12, -9, -0.1, (0.6, 0.1))   # tools “有限的”两下

# Approve：按下都有点击；停工前的每次点击带一个小“批准”音，停工后的只剩点击
approve_ok = [58.6, 59.7, 60.5, 61.5]
for i, t in enumerate(approve_ok):
    place(click(), t, -7, 0.35, (0.6, 0.1))
    place(beep(m(['D5', 'E5', 'F#5', 'A5'][i]), 0.14, 0.15), t + 0.06, -8, 0.35, (1.2, 0.2))
for t in [64.5, 65.15, 66.5, 68.5]:
    place(click(), t, -7, 0.35, (0.4, 0.06))
place(beep(m('A4'), 0.22, 0.4), 69.0, -5, 0, (1.0, 0.15)); place(beep(m('D4'), 0.45, 0.4), 69.25, -5, 0, (1.4, 0.2))   # 额度已耗尽

# ================= 71.4–89 控制台 =================
place(tick(0.04, 2600), 71.45, -8, 0, (0.8, 0.12))                                           # 控制台出现
for i in range(16): place(tick(0.03, 2200 + 120 * (i % 5)), 73.6 + i * 0.06 + 0.02 * rng.random(), -14, -0.9 + 0.12 * i, (0.8, 0.15))   # 拉远：许多个“上帝”的控制台
place(gliss(m('A4'), m('A5'), 0.7), 78.25, -8, 0, (1.6, 0.3))                                      # 额度已恢复
for t in [79.73, 81.03]:
    place(click(), t, -7, 0.2, (0.6, 0.1)); place(beep(m('D5'), 0.12, 0.15), t + 0.06, -9, 0.2, (1.0, 0.2))
place(toggle(), 84.0, -2, 0.2, (0.8, 0.12)); place(beep(m('D5'), 0.1, 0.2), 84.12, -8, 0.2); place(beep(m('A5'), 0.16, 0.2), 84.24, -8, 0.2)   # bypass 开关

# ================= 84.95–98 第二个循环：代理自行执行（无人看管，一直走进伊甸园） =================
L2 = Bus(DUR); B3 = 60 / 112; T2 = 84.95; END2 = 98.0
arp = ['D4', 'A4', 'F4', 'A4', 'D5', 'A4', 'F4', 'A4', 'C4', 'G4', 'E4', 'G4', 'C5', 'G4', 'E4', 'G4']
i = 0
while T2 + i * B3 / 4 < END2:
    t = T2 + i * B3 / 4
    L2.add(pluck(m(arp[i % 16]), 0.35, 0.25 + 0.2 * (i % 4 == 0), 0.990), t, 0.22 if i % 4 == 0 else 0.14, -0.4 + 0.8 * ((i * 5) % 16) / 15)
    if i % 16 == 0: L2.add(bass(m('D2') if (i // 16) % 2 == 0 else m('C2'), 4 * B3 * 0.95, r=0.3), t, 0.06)
    i += 1
l2 = reverb(L2.x, 1.2, 0.18)
fade = np.ones(l2.shape[1]); tt = np.arange(l2.shape[1]) / SR
fade *= np.clip((tt - T2) / 0.6, 0, 1)                                                       # 进场
fade *= np.where(tt > 89.0, 10 ** (-7 / 20), 1.0) * 0 + np.interp(tt, [88.6, 89.6], [1.0, 10 ** (-7 / 20)])   # 进伊甸园后退到远处
fade *= np.where(tt >= END2, 0, 1)                                                            # 咬果实时断开
l2 = l2 * fade
l2[:, int(89.3 * SR):] = lp(l2[:, int(89.3 * SR):], 1600)                                     # 远处：像隔壁房间
out.x += level_bus(l2, 85.5, 88.5, -6)
for t in [86.13, 86.4, 86.67, 87.7, 87.97]:                                                   # 一行行“已执行”
    place(beep(m('A5'), 0.06, 0.1), t, -12, 0.3, (0.6, 0.1))

# ================= 89–123 伊甸园 =================
place(pluck(m('D4'), 2.0, 0.3), 89.4, -9, -0.2, (2.4, 0.35))                                  # 萌芽
place(pluck(m('A4'), 1.6, 0.3), 91.8, -10, 0.1, (2.4, 0.35))
place(gliss(m('D4'), m('D6'), 1.8), 95.0, -8, 0.1, (2.4, 0.4))                                      # 藤蔓顺着节点爬上云端
place(beep(m('E5'), 0.1, 0.2), 96.85, -7, 0.2, (1.0, 0.15)); place(beep(m('A5'), 0.14, 0.2), 96.98, -7, 0.2, (1.0, 0.15))   # 已连接
place(crunch(), 98.05, -1, -0.1, (0.6, 0.08))                                                 # 咬一口
# 本地蒸馏：上行拨弦越来越密 → 开成 D 大和弦
dl = Bus(DUR)
ts = [99.2]
while ts[-1] < 105.7: ts.append(ts[-1] + max(0.09, 0.55 * 0.9 ** len(ts)))
for i, t in enumerate(ts):
    dl.add(pluck(m(['D4', 'F#4', 'A4', 'D5', 'E5', 'F#5', 'A5', 'D6'][i % 8]) + (12 if i > 24 else 0), 1.0, 0.5), t, 0.12 + 0.004 * i, -0.6 + 1.2 * ((i * 7) % 11) / 10)
dl.add(pad([m('D3'), m('A3'), m('D4'), m('F#4'), m('A4'), m('E5')], 6.4, a=1.2, r=0.15, cutoff=900, cutoff_end=3500), 105.6, 0.5)
d1 = reverb(dl.x, 2.6, 0.4)
d1[:, int(111.9 * SR):] = 0                                                                   # 撤销访问：掐断（混响尾巴一起没）
out.x += level_bus(d1, 106, 109, -5)
place(stamp([m('D3'), m('G#3')]), 111.9, -1, 0, (2.2, 0.3))                                   # 灭灯的一声闷击（三全音）
place(beep(m('A5'), 0.09, 0.45), 113.85, -6, 0.15, (0.8, 0.12)); place(beep(m('A5'), 0.09, 0.45), 114.05, -6, 0.15, (0.8, 0.12))   # 检测到可疑信号
for i, t in enumerate([117.0, 117.9, 118.7]): place(pluck(m(['A3', 'F3', 'D3'][i]), 1.2, 0.2), t, -12, -0.3 + 0.3 * i, (1.6, 0.25))   # 后代：一个个落下的小音
place(church_bell(m('D3'), 5.0), 121.35, -2, 0, (3.0, 0.4))                                  # 这叫原罪

n = int(DUR * SR); mix = out.x[:, :n]
mix *= np.clip((DUR - np.arange(n) / SR) / 1.0, 0, 1)
wavfile.write(__file__.replace('ch1_seq.py', 'ch1-seq-music.wav'), SR, mix.T.astype(np.float32))
print('ok', round(n / SR, 2), 'peak', round(float(np.abs(mix).max()), 3))
