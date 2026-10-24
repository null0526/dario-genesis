"""第五章后半（全片的结尾）声音层。全片 593.40–681.67 秒；全片秒 = 章内秒 + 518.1333。调式 D。
画面事件时间：5-7/5-8 来自 experiments/ch5-appeal/shot.html 的 EV（章内秒，由 outputs/chapter5-voice/data.js 的字级时间算出），
5-9/5-10 来自 experiments/ch5-ending/timing.json；都已在 全片-r3.mp4 上用 kit.frame_trace 核过（按钮按下 629.37、选择器出现 622.5、停用页 672.67 等）。

整段的构思：声音随希望一起被收走。
  暖（循环做减法）→ 钟（耶稣，原样回钟）→ 钟摆停住、四度和弦悬着不解决 → 通知提示音 → 静 → 停用页只剩一个很轻的平台单音。

  593.40–599.6   联合国→工单：灯一排排亮＝一串上行小音（D 大调，西方语境，收在玻璃 D6）；弧线拉平、工单卡浮出（597.58）＝一声低木头 D3
  600.00–629.37  ★循环 A（交还）88 BPM，D 大调，Bm–G–A–D 轮转（最后一小节落在 A 上，悬着）；低音＋电钢琴分解和弦＋每小节头一个玻璃音
                 “每交出一样东西，循环就少一个音”：对撞机灯环熄→玻璃声部撤走；聚变装置冷却→砍掉第 8 拍；火星轨迹收回→第 6 拍；
                 圆周率纬线淡去→第 4 拍；数据中心熄灯→第 2 拍；黄金升空离开→第 7 拍；套餐 Pro→Max20x→第 3 拍（这一下用平台提示音代替告别音）；
                 “恳请”，地球缩成太阳系→第 5 拍；循环只剩低音＋每小节一个音。每次告别＝在事件那一拍多放一个高八度的音（并进循环，同一件乐器）。
                 629.37 光标按下“提交申诉”＝一刀切断（停在 A 上，不解决）。点击有声：点击（rel -8，再大刺耳）＋一声冷提示。
  629.60         光包：D 大和弦（把悬着的 A 接到 D，是全段唯一温暖的解决）
  632.07         光包被黑洞吃进去：低木头 D3，一声
  632.76–641.45  ★循环 B（等待）60 BPM 的钟摆：低音 D3/A2＋一高一低两种滴答；635.76（第 3 天）加一个中音区木槌声部；
                 638.7 耶稣复核记录出现：教堂钟 D4（与第一章“耶稣”同音同轻，循环让路）；639.3 起钟摆越走越慢（第二章是越转越快），
                 在 641.47 已等待 72:00 越过的那一刻彻底停住——
  641.55         G 大和弦（第一章“已恢复”阿们终止的前半句 IV），不给 D：该来的“恢复”没来
  642.4–649.0    留白（旁白在讲两千年；画面只有盘慢转）
  649.03         第 7 天：低木头 D3 一声（钟摆最后的余响）
  653.07         邮箱亮：两声平台提示音 A5→D6（原样片里那声通知音的重做）
  654.42         邮件展开：一声很轻的纸
  654.8–672.07   邮件读完、停留、淡黑：全部留白
  672.70         停用页硬切：一个很轻的平台单音 D5（PAGE_TONE=False 则整页全静）；之后到片尾 681.67 全静"""
import os, sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

PAGE_TONE = True
DUR = 684.0
out = Bus(DUR)
_place = make_place(out)
LOG = []
T0 = 593.40
TEND = 681.67


def place(sig, t, rel=0.0, pan=0.0, verb=(1.6, 0.22)):
    LOG.append((round(float(t), 2), rel))
    return _place(sig, t, rel, pan, verb)


def at(t, what=''):
    assert t >= T0 - 1e-6, (t, what)
    return t


def cutoff(x, t_cut, fade=0.012):
    i = int(t_cut * SR); n = int(fade * SR)
    y = x.copy(); y[:, i:i + n] *= np.linspace(1, 0, n); y[:, i + n:] = 0
    return y


def ease(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def epb(note, dur=0.8, decay=0.30):
    """短电钢琴音：衰减比 ep 快，循环里八分音不糊。"""
    n = int(dur * SR); t = np.arange(n) / SR
    return ep(note, dur)[:n] * np.exp(-t / decay)


def blip(note, dur=0.5, decay=0.16):
    n = int(dur * SR); t = np.arange(n) / SR
    return mallet(note, dur)[:n] * np.exp(-t / decay)


# =============== 5-7：联合国 → 工单（593.40–599.6） ===============
# 14 排席位灯从里往外亮（593.40+：lights 从 594.10 起，每排 0.11 秒）：隔排取 8 个，间隔 0.2 秒 → 一串上行小音（D 大调完整音阶，含 G 与 C#）
for i, nm in enumerate(['D4', 'F#4', 'A4', 'D5', 'E5', 'G5', 'A5', 'C#6']):
    place(pluck(m(nm), 0.9, 0.55), at(594.24 + 0.2 * i), -12.5 + 0.3 * i, -0.5 + 0.14 * i, (1.3, 0.2))
place(glass(m('D6'), 2.4, 3.5, 1.0) + 0.6 * glass(m('A5'), 2.4, 3.5, 1.0), 595.90, -8, 0.1, (2.4, 0.35))   # 席位全亮：导音 C# 解决到 D
# 596.3–597.5 弧线拉直成表单横线（静默，只看）
place(knock_note(m('D3'), 1.4), 597.58, -8, 0.0, (1.8, 0.25))        # 横线刚好拉平、工单卡开始浮出（成片 597.6 起）：一声，两件事共用

# =============== 5-8 循环 A：交还（600.00–629.37） ===============
BPM_A = 88; BEAT = 60 / BPM_A; E8 = BEAT / 2; TB0 = 600.0; TB1 = 629.37
CHORDS = [  # (低音根, 低音五度, 分解和弦四音, 每小节头的玻璃音)
    ('D3', 'A2', ['D4', 'F#4', 'A4', 'D5'], 'A5'),     # I
    ('B2', 'F#3', ['D4', 'F#4', 'B4', 'D5'], 'F#5'),   # vi
    ('G2', 'D3', ['D4', 'G4', 'B4', 'D5'], 'D6'),      # IV（用到 4 级）
    ('A2', 'E3', ['E4', 'A4', 'C#5', 'E5'], 'E5'),     # V（用到导音 C#）
]
SHIFT = 1   # 从 Bm 起转：Bm G A D Bm G A D Bm G A —— 最后一小节（627.27–）落在 A 上
PAT = [0, 1, 2, 1, 3, 2, 1, 2]
# 事件（吸附到八分音网格）：(时间, 画面, 砍掉哪个声部)
EVENTS = [
    (606.00, '对撞机灯环熄', 'glass'),
    (608.00, '聚变装置冷却', 7),
    (611.00, '火星轨迹收回', 5),
    (612.90, '圆周率纬线淡去', 3),
    (614.30, '数据中心熄灯', 1),
    (619.00, '黄金升空离开', 6),
    (623.20, '套餐 Pro→Max20x', 2),      # 这一下用平台提示音代替告别音
    (625.40, '“恳请”地球缩成太阳系', 4),
]
snap = lambda t: TB0 + round((t - TB0) / E8) * E8
DEAD = {}   # 声部 -> 死亡时刻
FAREWELL = []
for te, _, what in EVENTS:
    ts = snap(te); DEAD[what] = ts
    if (te < 623.0 or te > 624.0) and what != 3:      # 623.2 用平台提示音代替；圆周率纬线淡去（缓慢、无集中事件）只砍声部，不放告别音
        FAREWELL.append(ts)

LA = Bus(DUR)
k = 0
while TB0 + k * E8 < TB1 - 1e-6:
    t = TB0 + k * E8; bar, pos = divmod(k, 8)
    root, fifth, tones, gl = CHORDS[(bar + SHIFT) % 4]
    if pos == 0:
        LA.add(bass(m(root), 1.5 * BEAT), t, 0.15)
        if t < DEAD['glass'] - 1e-6:
            LA.add(glass(m(gl), 1.6, 3.5, 0.8), t, 0.07, -0.3)
    if pos == 4:
        LA.add(bass(m(fifth), 1.2 * BEAT), t, 0.12)
    if t < DEAD.get(pos, 1e9) - 1e-6:
        LA.add(epb(m(tones[PAT[pos]]), 0.8, 0.30), t, 0.22, -0.35 + 0.7 * pos / 7)
    k += 1
for ts in FAREWELL:      # 告别音：这一拍的和弦音高八度，比平时亮一点、长一点（并进循环）
    bar = int((ts - TB0) // (8 * E8)); tones = CHORDS[(bar + SHIFT) % 4][2]
    pos = int(round((ts - TB0) / E8)) % 8
    LA.add(blip(m(tones[PAT[pos]]) + 12, 1.0, 0.34), ts, 0.30, 0.25)
la = reverb(LA.x, 1.2, 0.15)
la = level_bus(la, 601.0, 606.0, -6.5)
out.x += cutoff(la, TB1, 0.012)                                    # 629.37 光标按下：一刀切断（停在 A 上）

place(beep(m('A5'), 0.12, 0.35), 623.20, -9, 0.2, (0.9, 0.12))      # 套餐选择器移到 Max 20x：平台提示音（循环此时只剩半拍子，高音区不打架）

# 629.37 “提交申诉”：点击有声
place(click(), 629.37, -8, 0.2, (0.6, 0.1))
place(beep(m('D5'), 0.14, 0.15), 629.43, -9, 0.2, (1.2, 0.2))
# 629.57–629.87 太阳系收成光包：D 大和弦（接住悬着的 A，全段唯一的温暖解决）
pk = pad([m('D3'), m('A3'), m('D4'), m('F#4'), m('A4')], 1.6, a=0.12, r=1.1, cutoff=1000, cutoff_end=3000)
place(pk, 629.60, -6, 0, (2.6, 0.4))
place(glass(m('D6'), 2.4, 3.5, 1.0) + 0.7 * glass(m('A6'), 2.4, 3.5, 1.0), 629.62, -9, 0.1, (2.4, 0.35))

# =============== 5-9 光包进黑洞（630.2–） ===============
# 630.2–632.0 观测室、小信封、光包飞入：静默
place(knock_note(m('D3'), 1.6), 632.07, -6, 0.0, (2.2, 0.3))       # 视界吞没光包：低木头一声（盘亮度峰值）

# ---- 循环 B：钟摆 632.76–641.45 ----
TW0 = 632.76; TW1 = 641.45; T_DAY3 = 635.76; T_BELL = 638.68
LW = Bus(DUR)
BASS_W = ['D3', 'A2', 'D3', 'A2']
HOPE = ['D4', 'F#4', 'A4', 'F#4']


def rate(t):          # 639.3 起越走越慢，641.45 停住
    return 1.0 - ease((t - 639.3) / 2.15)


ph, t, kk, nxt, dt = 0.0, TW0, 0, 0.0, 0.002
while t < TW1:
    if ph >= nxt:
        pos = kk % 4
        if pos == 0: LW.add(bass(m(BASS_W[0]), 1.4), t, 0.17)
        if pos == 2: LW.add(bass(m(BASS_W[1]), 1.2), t, 0.13)
        if pos in (1, 3): LW.add(tick(0.04, 3000 if pos == 1 else 2100), t, 0.10, 0.3 if pos == 1 else -0.3)
        if pos == 0: LW.add(tick(0.04, 1500), t, 0.05, 0.0)
        if t >= T_DAY3 - 0.01:      # 第 3 天：加一个中音区木槌声部，落在拍外
            LW.add(blip(m(HOPE[kk % 4]), 0.6, 0.2), t + (0.0 if abs(t - T_DAY3) < 0.01 else 0.5 * (1.0 / max(rate(t), 0.2))), 0.18, 0.3)
        kk += 1; nxt += 1.0
    ph += rate(t) * dt; t += dt
lw = reverb(LW.x, 1.0, 0.12)
duck = np.interp(np.arange(lw.shape[1]) / SR, [T_BELL - 0.1, T_BELL + 0.05, T_BELL + 0.9, T_BELL + 1.5], [1.0, 10 ** (-7 / 20), 10 ** (-7 / 20), 1.0])
lw = level_bus(lw * duck, 633.0, 638.0, -7.5)
out.x += cutoff(lw, TW1, 0.05)                                       # 越过 72:00 的那一刻停住

place(church_bell(m('D4'), 4.0), T_BELL, -7, 0, (2.8, 0.4))          # 耶稣复核记录出现：轻钟（第一章“耶稣”同音）
g_ch = pad([m('G2'), m('D3'), m('G3'), m('B3'), m('D4')], 3.0, a=0.40, r=2.2, cutoff=900, cutoff_end=2200)
place(g_ch, 641.55, -7, 0, (2.8, 0.4))                                 # 第一章“已恢复”阿们终止的前半句 IV；这次不给 I

# 642.4–649.0 留白
place(knock_note(m('D3'), 1.4), 649.03, -10, 0.0, (1.8, 0.25))        # 第 7 天：钟摆最后的余响
place(beep(m('A5'), 0.12, 0.35), 653.07, -7, 0.1, (1.0, 0.15))        # 邮箱亮：两声平台提示音（A5→D6）
place(beep(m('D6'), 0.30, 0.35), 653.23, -6, 0.1, (1.4, 0.2))
place(paper(0.5, 900, 3500), 654.42, -10, 0.0, (0.8, 0.12))           # 提示条展开成全文
# 654.8–672.07 留白（邮件读完、停留、淡黑）
if PAGE_TONE:
    place(beep(m('D5'), 0.20, 0.3), 672.70, -13, 0.0, (1.6, 0.25))    # 停用页：一个很轻的平台单音

# ---------- 输出 ----------
n = int(DUR * SR)
mix = out.x[:, :n].copy()
mix[:, :int(T0 * SR)] = 0
mix[:, int(TEND * SR):] = 0
print('--- 循环区间内的点缀（place 登记；循环自己的告别音、钟摆声部不算点缀）---')
for nm, (a, b) in {'A': (TB0, TB1), 'B': (TW0, TW1)}.items():
    pts = sorted(t for t, rel in LOG if a <= t <= b)
    close = [(x, y) for i, x in enumerate(pts) for y in pts[i + 1:] if y - x < 2.0]
    print(nm, (a, b), 'n =', len(pts), pts, '2秒内成对:', close)
print('告别音（吸附后）:', [round(x, 2) for x in FAREWELL])
wavfile.write(__file__.replace('ch5_part_b.py', 'ch5-part-b-music.wav'), SR, mix.T.astype(np.float32))
pk = peaks_per_second(mix)
print('ok', round(n / SR, 2), 'peak', round(float(np.abs(mix).max()), 3))
print({i: p for i, p in enumerate(pk) if p > 0.001})
