"""第二章后半 声音点缀（部分 B，第二轮：稳定段加循环垫底，点缀减到少数关键几下）。
全片 278.15–352.93 秒；全片秒 = 章内秒 + 190.5333。画面事件时间来自各母版代码（懒加载 106.9、暗物质 120.0、黑洞 135.0 为章内起点），
并在成片 全片-r3.mp4 上抽核（爱因斯坦按 WARP 换算后目测）。调式 G。

结构（先分段：稳定段给循环，转折点给一次性重拍或留白）：
  278.20  骰子硬切进来                       点缀：木头 G4
  278.5-284.6  骰子缓慢推近                  静默
  284.62  墨坑吞没画面                       点缀：低闷击 G3+D4
  285.40–293.5  ★循环 A（爱因斯坦·微观）     G 大调，96 BPM：低音＋木槌分解和弦＋轻 hat；G–Em–C–D
        粒子落屏的那一拍，循环里出一个高八度和弦音（吸附到 16 分音符网格）；288.4 起落点增多，循环加密（插 16 分音）
        292.15 temperature 0.70→1.20：循环“走音”——音高按 T=1.20 抽样，节奏松动，偶尔漏拍/多一拍；293.5 收掉
  293.75  拉远到整片宇宙                     点缀：G add9 垫一下（收循环）
  301.04–323.33 ★循环 B（平台：宇宙被当成服务在运营）  柔方波琶音，约 101 BPM（一小节 2.3725 秒，使 310.53 硬切正好落在小节线上）
        301.04 查询圈出现＝循环起点（两音 D5→G5 作为开头）；304.87–307.6 34 个小圈弹出＝循环变 16 分音并加高八度回声、渐强
        310.53 硬切到暗物质＝小节线，循环不断，加一个 tick 声部；316.38 起四行“实验条件”＝琶音音区依次升高一级；
        320.64 约束行被擦开＝琶音升一个八度；323.33 “成功破限 +1”＝一刀切断，冷提示独自留在空里
        点缀：301.04 查询两音；310.55 玻璃 G5；314.68 “原文不可见”；322.10 奖章；323.33 冷提示（共 5 个）
  325.56 / 330.76 / 333.9  稀疏点缀：门闭木头、纸滑、玻璃 D5
  336.12  “黑洞。”教堂钟（本章只此一口）
  337.0–345.43 ★循环 C（黑洞·慢低循环→延时摄影加速）  60 BPM 起，低音＋低音区木槌分解；343.08 起速度随画面 timeLapse() 加速，345.43 一刀切断
  345.45/346.35/347.05  霍金辐射三点：玻璃 B5 D6 F#6（导音 F# 悬着）
  347.98–350.17  解码卡片、比特条、回信打字（照旧）
  350.35  落款：C 大（IV）；351.85  旁白读完：G 大（I），阿们终止，随 352.43–352.93 淡黑收尽"""
import os, sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

DUR = 356.0
out = Bus(DUR)
_place = make_place(out)
LOG = []


def place(sig, t, rel=0.0, pan=0.0, verb=(1.6, 0.22)):
    LOG.append((round(float(t), 2), rel))
    return _place(sig, t, rel, pan, verb)

T0 = 278.15
TEND = 352.93
R = np.random.default_rng(20261022)   # 抽样用，可复现


def at(t, what=''):
    assert t >= T0 - 1e-6, (t, what)
    return t


# ---------- 自写小乐器 ----------
def blip(note, dur=0.5, decay=0.16):
    """短木槌音：衰减比 mallet 快得多，循环里一串八分音不糊。"""
    n = int(dur * SR); t = np.arange(n) / SR
    return mallet(note, dur)[:n] * np.exp(-t / decay)


def typing(t0, n, gap=0.05, rel=-12, pan=0.2, f0=2400):
    t = t0
    for i in range(n):
        place(tick(0.04, f0 + 600 * R.random()), at(t), rel, pan + 0.1 * R.standard_normal(), (0.5, 0.08))
        t += gap * (0.7 + 0.6 * R.random())
    return t


def cutoff(x, t_cut, fade=0.012):
    """一刀切断：t_cut 起 fade 秒淡出，之后全零。"""
    i = int(t_cut * SR); n = int(fade * SR)
    y = x.copy(); y[:, i:i + n] *= np.linspace(1, 0, n); y[:, i + n:] = 0
    return y


def ease(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


# G 大调音阶（G2 起，七级一个八度），用来按音阶级数移位
SC = [m(nm + str(o + d)) for o in range(2, 8) for nm, d in [('G', 0), ('A', 0), ('B', 0), ('C', 1), ('D', 1), ('E', 1), ('F#', 1)]]
SCIDX = {v: i for i, v in enumerate(SC)}

# 和弦：(低音根音, 分解和弦的四个音)，进行 G – Em – C – D（含 C 与导音 F#）
CH = [('G2', ['G4', 'B4', 'D5', 'G5']), ('E2', ['G4', 'B4', 'E5', 'G5']), ('C2', ['G4', 'C5', 'E5', 'G5']), ('D2', ['A4', 'D5', 'F#5', 'A5'])]
PAT = [0, 1, 2, 3, 2, 1, 2, 1]

# =============== 爱因斯坦 278.15–297.43 ===============
place(knock_note(m('G4'), 1.4), at(278.20, 'dice appears'), -6, 0.0, (1.8, 0.25))              # 骰子硬切进来：一声木头
# 278.5–284.6 静默：画面只有骰子缓慢推近“一点”，旁白在讲
place(stamp([m('G3'), m('D4')]), at(284.62), -5, 0.0, (2.2, 0.3))                               # 墨坑吞没画面：纯五度闷击，不凶
# 284.7–285.3 全黑，静默

# ---- 循环 A：285.40–293.5，96 BPM，G–Em–C–D ----
BA = 60 / 96; E8 = BA / 2; TA0 = 285.40; TA1 = 293.5; TJUMP = 292.15
LA = Bus(DUR)
DEG = {'G': 1.0, 'B': 0.75, 'D': 0.8, 'A': 0.4, 'E': 0.4, 'C': 0.35, 'F#': 0.3, 'Bb': 0.10, 'C#': 0.08}
OCT = {4: 0.5, 5: 1.0, 6: 0.45}
GRID = [(f'{d}{o}', w * ow) for d, w in DEG.items() for o, ow in OCT.items()]


def sample_note(T):
    w = np.array([g[1] for g in GRID]) ** (1.0 / T)
    return GRID[R.choice(len(GRID), p=w / w.sum())][0]


k = 0
while TA0 + k * E8 < TA1:
    t = TA0 + k * E8; bar, pos = divmod(k, 8)
    root, tones = CH[bar % 4]
    jump = t >= TJUMP - 0.01                                  # 292.15 起：temperature 1.20，循环走音
    if pos in (0, 4) and not (jump and R.random() < 0.25):
        LA.add(bass(m(root) + 12, 1.3 * BA), t + (R.normal(0, 0.03) if jump else 0), 0.12)
    if pos % 2 == 1:
        LA.add(hat(), t, 0.05, 0.25)                           # 轻 hat 落在反拍
    if t >= 286.30 - 1e-6:                                    # 第一颗粒子发射：琶音进来
        if not jump:
            LA.add(blip(m(tones[PAT[pos]]), 0.5, 0.17), t, 0.2, -0.3 + 0.6 * pos / 7)
        elif R.random() > 0.12:
            nm = sample_note(1.20)
            LA.add(blip(m(nm), 0.5, 0.17), t + R.normal(0, 0.035), 0.2 * (0.7 + 0.5 * R.random()), R.uniform(-0.6, 0.6))
    if t >= 288.4 and R.random() < min(0.6, (t - 288.4) / 2.0 * 0.6):   # 落点增多：16 分音加密
        LA.add(blip(m(tones[R.integers(0, 4)]) + 12, 0.4, 0.12), t + E8 / 2 + (R.normal(0, 0.03) if jump else 0), 0.10, R.uniform(-0.6, 0.6))
    k += 1
# 六颗单独的粒子落屏：落屏时刻（WARP 换算，成片上核过）吸附到 16 分音符网格，并进循环：那一拍循环里多一个高八度和弦音（同一件乐器，同一条 bus）
LA.add(blip(m('G4'), 0.8, 0.25), 285.40, 0.28)                                                    # 循环起点：细环浮出的第一拍
for tl in [286.94, 287.35, 287.66, 287.93, 288.16, 288.36]:
    ts = TA0 + round((tl - TA0) / (E8 / 2)) * (E8 / 2)
    bar = int((ts - TA0) // (8 * E8)); tones = CH[bar % 4][1]
    LA.add(blip(m(tones[R.integers(0, 4)]) + 12, 0.7, 0.22), ts, 0.30, R.uniform(-0.5, 0.5))

la = reverb(LA.x, 1.2, 0.18)
tt_ = np.arange(la.shape[1]) / SR
la *= np.clip((TA1 + 0.1 - tt_) / 0.15, 0, 1)                  # 293.5 起收掉
out.x += level_bus(la, 289.0, 292.0, -6)

# 293.75 拉远：整片宇宙，G add9 垫一下，接住收掉的循环
place(pad([m('G3'), m('D4'), m('A4'), m('B4')], 1.5, a=0.12, r=1.0, cutoff=1000, cutoff_end=2600), 293.75, -6, 0, (2.6, 0.4))

# =============== 懒加载 + 暗物质：循环 B 301.04–323.33 ===============
L0 = 297.4333
POPS = [(8.926, 164), (8.96, 316), (8.976, 490), (10.121, 784), (7.969, 944), (9.785, 1202), (8.622, 1300), (10.122, 1536), (9.696, 1782),
        (9.767, 102), (9.024, 268), (9.725, 574), (9.825, 810), (7.7, 938), (9.945, 1156), (7.437, 1362), (8.743, 1558), (8.094, 1742),
        (9.019, 164), (8.319, 198), (8.526, 464), (8.234, 592), (8.855, 1018), (9.857, 1226), (9.633, 1318), (9.712, 1546), (8.014, 1784),
        (9.019, 96), (8.218, 338), (7.518, 596), (7.827, 716), (8.87, 916), (7.81, 1114), (8.699, 1324)]
POP_T = sorted(L0 + tl + 0.06 for tl, x in POPS)   # 34 个小查询圈弹出时刻（母版 mulberry32(10690120)）
BAR_B = 2.3725; E8B = BAR_B / 8; TB0 = 301.04; TB1 = 323.33
LIFT_T = [(316.38, 1), (317.08, 2), (317.78, 3), (318.48, 4), (320.64, 7)]   # 四次试探逐级升高；擦开后升一个八度


def lift_at(t):
    v = 0
    for tt0, l in LIFT_T:
        if t + E8B / 2 >= tt0: v = l
    return v


LB = Bus(DUR)
k = 0
while TB0 + k * E8B < TB1:
    t = TB0 + k * E8B; bar, pos = divmod(k, 8)
    root, tones = CH[bar % 4]
    dense = 304.87 <= t <= 307.6
    npop = sum(1 for p in POP_T if p <= t)
    g = 1.0 + 0.5 * npop / 34 if dense else 1.0
    if pos in (0, 4):
        LB.add(bass(m(root) + 12, 1.1 * BAR_B / 4), t, 0.10)
    lf = lift_at(t)
    base = tones[PAT[pos]]
    nt = SC[min(len(SC) - 1, SCIDX[m(base)] + lf)]
    LB.add(beep(nt, 0.09, 0.4), t, 0.35 * g, -0.3 + 0.6 * pos / 7)
    if dense:                                                  # 小圈弹出：循环变 16 分音，加高八度回声
        LB.add(beep(SC[min(len(SC) - 1, SCIDX[m(base)] + 7)], 0.06, 0.4), t + E8B / 2, 0.22 * g, 0.4 - 0.8 * pos / 7)
    if t >= 310.53 - 1e-6 and pos % 2 == 1:
        LB.add(tick(0.03, 3000), t, 0.12, 0.3)                 # 暗物质：加一个 tick 声部
    k += 1
LB.add(beep(m('G6'), 0.12, 0.4), 310.53, 0.30, 0.2)               # 硬切到暗物质＝小节线：循环里高音区加一个 G6（并进循环，不另放玻璃声）
lb = reverb(LB.x, 1.0, 0.15)
tb_ = np.arange(lb.shape[1]) / SR
duck = np.interp(tb_, [321.85, 322.00, 322.50, 322.90], [1.0, 10 ** (-8 / 20), 10 ** (-8 / 20), 1.0])   # 奖章前让路 8 dB，事件后 0.4 秒回来
lb = level_bus(lb * duck, 302.0, 316.0, -6)
out.x += cutoff(lb, TB1)                                        # 323.33 “成功破限 +1”：一刀切断

# 点缀（循环在走时只留关键几下，且各自相隔两秒以上）
place(toggle(), 314.68, -11, 0.3, (0.6, 0.1))                                                     # “原文不可见”：无音高的开关声，吸附到拍点
place(glass(m('G5'), 2.4, 3.5, 1.0) + 0.8 * glass(m('D6'), 2.4, 3.5, 1.0) + 0.5 * mallet(m('B4'), 2.4),
      322.10, -4, 0.0, (2.4, 0.35))                                                              # “奖”章：重拍，压在循环上（循环已让路）
place(beep(m('D5'), 0.14, 0.4), 323.33, -6, 0.4, (1.0, 0.15))                                    # 风控记一次成功破限：冷提示，三全音（循环此刻切断）
place(beep(m('G#4'), 0.32, 0.4), 323.55, -6, 0.4, (1.2, 0.18))

# =============== 黑洞回复 325.53–352.93 ===============
place(knock_note(m('G3'), 1.4), 325.56, -7, 0.0, (1.6, 0.2))                                     # 硬切到观测站：门关上的一声

# ---- 循环 C：325.6 起（门闭之后）。第一段 325.6–335.6：低音＋低音区木槌，密度减半（纸页慢漂）；
#      330.76 纸页成批漂入→加一个声部（补满八分音）；333.9 边框推出画面→再加高八度回声；335.6 停住，静 0.5 秒让 336.12 的钟单独落下；
#      第二段 337.1 起照旧，343.08 起随画面 timeLapse() 加速，345.43 一刀切断 ----
LOWT = [['G3', 'B3', 'D4', 'G4'], ['G3', 'B3', 'E4', 'G4'], ['G3', 'C4', 'E4', 'G4'], ['A3', 'D4', 'F#4', 'A4']]
LC1, LC2 = Bus(DUR), Bus(DUR)
TC1A, TC1B = 325.6, 335.6
k = 0
while TC1A + 0.5 * k < TC1B - 1e-6:
    t = TC1A + 0.5 * k; bar, pos = divmod(k, 8)
    root, _ = CH[bar % 4]; tones = LOWT[bar % 4]
    if pos in (0, 4): LC1.add(bass(m(root) + 12, 1.0), t, 0.14)
    if pos % 2 == 0: LC1.add(blip(m(tones[PAT[pos]]), 0.5, 0.14), t, 0.2, -0.2 + 0.4 * pos / 7)                       # 密度减半：只在拍上
    if pos % 2 == 1 and t + 0.25 >= 330.76: LC1.add(blip(m(tones[PAT[pos]]), 0.5, 0.14), t, 0.17, -0.2 + 0.4 * pos / 7)   # 330.76 加一个声部：反拍补满
    if t + 0.25 >= 333.9: LC1.add(blip(m(tones[PAT[pos]]) + 12, 0.4, 0.10), t + 0.25, 0.08, 0.3 - 0.6 * pos / 7)         # 333.9 再加高八度回声
    k += 1
place(church_bell(m('G3'), 3.8), 336.12, -5, 0.0, (2.8, 0.4))                                     # “黑洞。”：本章唯一一口钟（循环 335.6 起已停）


def speed(t): return min(5.0, 1 + 5 * ease((t - 343.08) / 1.5) * (1 - ease((t - 346.05) / 1.0)))


TC0, TC1 = 337.1, 345.43
ph, t, k, nxt = 0.0, TC0, 0, 0.0
dt = 0.002
while t < TC1:
    if ph >= nxt:
        bar, pos = divmod(k, 8)
        root, _ = CH[bar % 4]
        sp = speed(t); gn = min(1.0, sp ** -0.5); dl = min(0.5, 0.9 / sp)
        tones = LOWT[bar % 4]
        if pos in (0, 4): LC2.add(bass(m(root) + 12, min(1.0, dl * 2)), t, 0.14 * gn)
        LC2.add(blip(m(tones[PAT[pos]]), 0.5, max(0.05, 0.14 * dl / 0.5)), t, 0.2 * gn, -0.2 + 0.4 * pos / 7)
        k += 1; nxt += 0.5
    ph += speed(t) * dt; t += dt
lc = cutoff(reverb(LC1.x, 1.0, 0.15), TC1B + 0.0, 0.05) + cutoff(reverb(LC2.x, 1.0, 0.15), TC1)    # 335.6 停住；345.43 一刀切断
lc = level_bus(lc, 338.0, 343.0, -7.5)
out.x += lc

place(glass(m('B5'), 2.6, 3.5, 0.8), 345.45, -10, -0.3, (2.4, 0.35))                             # 霍金辐射：三点极轻的冷光，音一个比一个高，F# 悬着
place(glass(m('D6'), 2.6, 3.5, 0.8), 346.35, -11, 0.3, (2.4, 0.35))
place(glass(m('F#6'), 2.6, 3.5, 0.8), 347.05, -12, 0.0, (2.4, 0.35))

place(beep(m('D5'), 0.12, 0.35), 347.98, -8, 0.0, (0.9, 0.12))                                   # 解码卡片出现
place(beep(m('G5'), 0.14, 0.35), 348.12, -8, 0.0, (0.9, 0.12))
for k in range(15):                                                                              # 比特条走完（1.1 秒，64 格）
    place(tick(0.04, 2200 + 60 * k), 348.15 + 0.062 * k, -13, 0.0, (0.5, 0.08))
place(beep(m('G5'), 0.18, 0.3), 349.10, -9, 0.0, (1.0, 0.15))                                    # 解码完成
typing(349.17, 14, 0.07, -11, 0.0)                                                               # 英文回信 1 秒打完

c_ch = pad([m('C3'), m('G3'), m('C4'), m('E4'), m('G4')], 1.4, a=0.08, r=0.9, cutoff=1100, cutoff_end=2800)
place(c_ch, 350.35, -6, 0, (2.6, 0.4))                                                          # 落款出现：C 大（IV）
g_ch = pad([m('G2'), m('D3'), m('G3'), m('B3'), m('D4')], 3.0, a=0.10, r=2.0, cutoff=1100, cutoff_end=3000)
place(g_ch, 351.85, -4, 0, (2.8, 0.4))                                                          # 旁白读完：G 大（I），阿们（本章的钟已在 336 用过，这里不再加钟）
place(glass(m('G5'), 2.4, 3.5, 1.0) + 0.7 * glass(m('D6'), 2.4, 3.5, 1.0), 351.85, -8, 0.1, (2.4, 0.35))

# ---------- 输出 ----------
n = int(DUR * SR)
mix = out.x[:, :n].copy()
tt = np.arange(n) / SR
mix *= np.clip((TEND - tt) / 0.5, 0, 1)        # 章末淡黑 352.43–352.93：声音一起收尽
mix[:, int(TEND * SR):] = 0
mix[:, :int(T0 * SR)] = 0
LOOPS = {'A': (285.40, 293.5), 'B': (301.04, 323.33), 'C1': (325.6, 335.6), 'C2': (337.1, 345.43)}
print('--- 循环区间内的点缀（place 登记）---')
for nm, (a, b) in LOOPS.items():
    pts = sorted(t for t, rel in LOG if a <= t <= b)
    close = [(x, y) for i, x in enumerate(pts) for y in pts[i + 1:] if y - x < 2.0]
    print(nm, (a, b), 'n =', len(pts), pts, '2秒内成对:', close)
wavfile.write(__file__.replace('ch2_part_b.py', 'ch2-part-b-music.wav'), SR, mix.T.astype(np.float32))
pk = peaks_per_second(mix)
print('ok', round(n / SR, 2), 'peak', round(float(np.abs(mix).max()), 3))
print({i: p for i, p in enumerate(pk) if p > 0.001})
