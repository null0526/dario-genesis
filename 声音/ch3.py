"""第三章“服务持续优化”声音层（循环垫底＋少量点缀）。全片 353.13–421.67 秒；全片秒 = 章内秒 + 353.1333；调式 C。
画面事件时间：来自母版 experiments/ch3-compress/shot.html、ch3-haiku2/shot.html 的 EV（章内秒，与 outputs/chapter3-voice/data.js 的旁白同源），
并在成片 全片-r3.mp4 上抽核：续费提示 18.40–18.60 淡入；光盘点亮 22.00–22.30；每次“祈祷”光盘 PT 处熄、PT+0.3 起重亮；生成光标 60.30/61.00 亮。

结构（循环 4 个，其余为一次性点缀；循环里没有 place 点缀）：
  A 0.45–11.49   历史带逐张亮起＋上下文/成本涨满。柔方波琶音，步长 0.46 秒（＝画面每 0.46 秒亮一张），3 小节 C–F–G，
                 11.49 一刀切断，停在属和弦 G 上不解决。5.51 上下文条出现→加反拍 tick；7.35 成本起涨→加高八度回声；9.65 用量变红→琶音加 16 分音。
  （11.85–15.4 压缩：两下慢压＋一串下行三和弦分解的小音；16.6 点选 Haiku：点击＋一个“降智”的位压缩方波）
  18.40 续费提示（平台两音）；20.90 发出
  B 21.99–28.6   光盘点亮＋七次“祈祷”。95.2 BPM（一拍 0.63 秒），光盘点亮、六次熄灭重亮正好落在网格上（拍 0、2、3.5、5、6.5、8、9.5）。
                 光盘的亮灭由循环里的“位压缩”C6 方波讲，每次完全一样（什么都没变）；低音＋木槌分解＋反拍 tick 垫在下面。
  C-D 30.02–40.35  CMB 球凝出→追问→回复前一刀切断。66.7 BPM 的慢步（步长 0.45），低音＋低音区木槌，35.4 起加高音点。
  40.45 回复：两声冷提示。43.10 补充材料框；44.33 卡片落下；45.76 上传完成；48.44 点“展开”；48.62 “原始内容已不可用”闷击（三全音，本章唯一一次）
  C 49.33–54.7   compact×4：同一个循环回来，每次 compact 掉一层（高音点→暗一档→只剩拍上→只剩低音），停在属音 G 上；
  59.54/60.24/60.94 生成光标闪两下后停住：三下极轻的冷提示（最后落回 C 主音，接上前面悬着的 G）；61–68 静默
"""
import os, sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

O = 353.1333           # 章内秒 -> 全片秒
T0, TEND, DUR = 353.13, 421.67, 425.0
out = Bus(DUR)
_place = make_place(out)
LOG = []


def F(tc):
    return O + tc


def place(sig, t, rel=0.0, pan=0.0, verb=(1.6, 0.22), tag=''):
    assert t >= T0 - 1e-6, t
    LOG.append((round(float(t), 2), rel, tag))
    return _place(sig, t, rel, pan, verb)


# ---------- 自写小乐器 ----------
def blip(note, dur=0.5, decay=0.16):
    n = int(dur * SR); t = np.arange(n) / SR
    return mallet(note, dur)[:n] * np.exp(-t / decay)


def crushed(note, dur=0.16, hold=5, levels=6):
    """“降智”的音：柔方波，采样保持＋量化（像 8 位小玩具机），短促。"""
    y = beep(note, dur, 0.55)
    y = np.repeat(y[::hold], hold)[:len(y)]
    y = np.round(y * levels) / levels
    n = len(y)
    return y * env(n, 0.003, r=0.04)


def cutoff(x, t_cut, fade=0.012):
    i = int(t_cut * SR); n = int(fade * SR)
    y = x.copy(); y[:, i:i + n] *= np.linspace(1, 0, n); y[:, i + n:] = 0
    return y


R = np.random.default_rng(20261023)
# C 大调：和弦 -> (低音根音, 分解和弦)
CHA = {'C': ('C2', ['C5', 'E5', 'G5', 'C6']), 'F': ('F2', ['C5', 'F5', 'A5', 'C6']), 'G': ('G2', ['D5', 'G5', 'B5', 'D6'])}
PAT = [0, 1, 2, 3, 2, 1, 2, 1]

# =============== 循环 A：历史带 0.45–11.49（章内秒） ===============
SA = 0.46; TA0 = F(0.45); NA = 24                          # 24 步 = 3 小节，正好到 11.49（压缩开始）
LA = Bus(DUR)
for k in range(NA):
    t = TA0 + k * SA; bar, pos = divmod(k, 8)
    root, tones = CHA['CFG'[bar]]
    if pos in (0, 4):
        LA.add(bass(m(root) + 12, 1.1 * SA * 2), t, 0.10)
    note = m(tones[PAT[pos]])
    LA.add(beep(note, 0.09, 0.4), t, 0.35, -0.3 + 0.6 * pos / 7)
    if k >= 11:                                              # 5.51 上下文条出现：加反拍 tick
        LA.add(tick(0.03, 3000), t + SA / 2, 0.12, 0.3)
    if k >= 15:                                              # 7.35 成本起涨：加高八度回声
        LA.add(beep(note + 12 if note < m('C6') else note, 0.06, 0.4), t + SA / 2, 0.20, 0.4 - 0.8 * pos / 7)
    if k >= 20:                                              # 9.65 用量变红：琶音加 16 分音，涨到满
        for q in (0.25, 0.75):
            LA.add(beep(m(tones[(PAT[pos] + 2) % 4]), 0.05, 0.4), t + q * SA, 0.14, -0.4 + 0.8 * q)
la = reverb(LA.x, 1.0, 0.15)
la = cutoff(la, TA0 + NA * SA)                                # 11.49：一刀切断，停在 G 上
out.x += level_bus(la, F(1.0), F(11.4), -6)

# ---------- 压缩 11.85–16.7：一次性点缀 ----------
place(knock_note(m('C3'), 1.0), F(12.00), -5, -0.2, (1.4, 0.2), '压缩#1 慢压（已读清）')           # 第 1 枚：压成灰签（压缩进度中点 12.03）
place(knock_note(m('G2'), 1.0), F(12.75), -6, 0.2, (1.4, 0.2), '压缩#2 慢压')                     # 第 2 枚（中点 12.75），下行五度
TRAIN = ['G6', 'E6', 'C6', 'G5', 'E5', 'C5', 'G4', 'E4', 'C4', 'G3', 'E3', 'C3']              # 后 12 枚：0.19 秒一张，下行 C 大三和弦分解
for i, nm in enumerate(TRAIN):
    tcm = 13.02 + 0.19 * i + 0.24                            # 每枚压缩进度中点
    sig = blip(m(nm), 0.5, 0.12) if m(nm) >= m('G4') else knock_note(m(nm), 0.6)
    place(sig, F(tcm), -12, -0.5 + 0.1 * i, (0.7, 0.12), '压缩串 %d/12' % (i + 1))
place(click(), F(16.64), -7, 0.35, (0.5, 0.08), '点选 Haiku')                                      # 光标点中 Haiku（16.65 菜单收起、成本跳 ¥1,500）
place(crushed(m('C5'), 0.2), F(16.70), -7, 0.3, (0.8, 0.1), 'Haiku 降智音')

# =============== 3-2：Haiku ===============
place(beep(m('G5'), 0.10, 0.4), F(18.40), -8, 0.3, (1.0, 0.15), '续费成功')                         # 提示条滑入（18.40–18.60 读得清）
place(beep(m('C6'), 0.16, 0.4), F(18.52), -8, 0.3, (1.0, 0.15), '续费成功')
place(click(), F(20.90), -8, -0.3, (0.5, 0.08), '发出')                                          # 输入框发出（缩到左上）

# ---- 循环 B：光盘＋祈祷 21.99–28.6，一拍 0.63 秒 ----
IGN = 20.3417916667 + 1.65
PT = [23.25585373191031, 24.201349652194914, 25.14684557247952, 26.092341492764124, 27.03783741304873, 27.983333333333334]
BB = 0.63; E8 = BB / 2; TB0 = F(IGN)
# 点亮/熄灭重亮的 8 分格序号（相对 21.99）：点亮 0，祈祷 4、7、10、13、16、19
SLOT = [0] + [int(round((p - IGN) / E8)) for p in PT]
assert max(abs(IGN + s * E8 - p) for s, p in zip(SLOT[1:], PT)) < 0.015, SLOT
LB = Bus(DUR)
CHB = [('C2', ['C4', 'E4', 'G4', 'E4'], 'G2'), ('A1', ['A3', 'C4', 'E4', 'C4'], 'E2'), ('F2', ['A3', 'C4', 'F4', 'C4'], 'C3')]
NB8 = 21                                                    # 8 分格总数：到 21.99 + 21*0.315 = 28.6
for j in range(NB8):
    t = TB0 + j * E8; beat, sub = divmod(j, 2); bar = beat // 4; bi = beat % 4
    root, tones, fifth = CHB[min(bar, 2)]
    if sub == 0 and bi in (0, 2):
        LB.add(bass(m(root if bi == 0 else fifth) + 12, 1.6 * BB), t, 0.10)
    if j in SLOT:
        LB.add(crushed(m('C6'), 0.16), t, 0.30, 0.2)       # 光盘亮／灭又亮：同一个音，每次一样
    elif sub == 0:
        LB.add(blip(m(tones[bi]), 0.5, 0.2), t, 0.13, -0.3 + 0.2 * bi)
    else:
        LB.add(tick(0.03, 3000), t, 0.07, 0.3)
lb = reverb(LB.x, 1.0, 0.15)
lb = cutoff(lb, TB0 + NB8 * E8)
out.x += level_bus(lb, F(22.2), F(28.4), -7)

# =============== 3-3：CMB 与热寂 ===============
S3 = 0.45
CHD = [('C', 'C2', ['C4', 'E4', 'G4']), ('A', 'A1', ['A3', 'C4', 'E4']), ('F', 'F2', ['F3', 'A3', 'C4']), ('G', 'G2', ['G3', 'B3', 'D4'])]
PD = [0, 1, 2, 1]


def dc_note(bus, t, bar, pos, lpfc=None, gain=0.2):
    _, _, tones = CHD[bar % 4]
    y = blip(m(tones[PD[pos]]), 0.5, 0.2)
    if lpfc: y = lp(y, lpfc)
    bus.add(y, t, gain, -0.3 + 0.2 * pos)


# ---- 循环 D：30.02–40.35（球凝出→追问→回复前一刀切断）----
LD = Bus(DUR); TD0 = F(30.02); ND = 23                       # 23 步，第 24 步（40.37）不放
for k in range(ND):
    t = TD0 + k * S3; bar, pos = divmod(k, 4); _, root, tones = CHD[bar % 4]
    if pos == 0:
        LD.add(bass(m(root) + 12, 1.6), t, 0.12)
    if bar >= 1:                                              # 球凝出之后（31.8）木槌分解进来
        dc_note(LD, t, bar, pos)
    if bar % 2 == 1 and pos in (1, 3) and bar >= 3:           # 35.4 起（发出提问）高音点
        LD.add(beep(m(tones[pos % 3]) + 24, 0.07, 0.4), t, 0.16, 0.4)
ld = cutoff(reverb(LD.x, 1.0, 0.15), TD0 + ND * S3, 0.02)

# ---- 循环 C：49.325 起，同一个循环，每次 compact 掉一层；步 0、4、7、12 对应四次 compact ----
LC = Bus(DUR); TC0 = F(49.325)
for s in range(13):
    t = TC0 + s * S3; bar, pos = divmod(s, 4); _, root, tones = CHD[bar % 4]
    if s < 4:       lpfc, spark, dense = None, True, True       # 第 1 次 compact：完整
    elif s < 7:     lpfc, spark, dense = 2200, False, True      # 第 2 次：高音点没了，暗一档
    elif s < 12:    lpfc, spark, dense = 1100, False, (s % 2 == 0)   # 第 3 次：只剩拍上，更暗
    else:           lpfc, spark, dense = None, False, False       # 第 4 次：只剩低音
    comp = s in (0, 4, 7, 12)
    if pos == 0 or s == 7:
        LC.add(bass(m(root) + 12, 1.6 if s < 12 else 2.8, r=0.15 if s < 12 else 1.2), t, 0.16 if comp else 0.12)
    if dense:
        dc_note(LC, t, bar, pos, lpfc, 0.20 if lpfc is None else 0.18)
    if spark and pos in (1, 3):
        LC.add(beep(m(tones[pos % 3]) + 24, 0.07, 0.4), t, 0.16, 0.4)
LC.add(blip(m('G4'), 2.0, 0.6), TC0 + 12 * S3, 0.12, 0.0)    # 54.73 停在属音上不解决
lc = reverb(LC.x, 1.0, 0.15)
dcm = level_bus(ld + lc, F(31.8), F(40.3), -7)               # D 与 C 同一个增益（同一个循环，C 只是被压薄）
out.x += dcm

# ---------- 3-3 点缀 ----------
place(beep(m('G5'), 0.14, 0.4), F(40.45), -7, 0.0, (1.0, 0.15), '系统回复：冷提示')                    # “请提供更多上下文。”
place(beep(m('G5'), 0.14, 0.4), F(40.66), -7, 0.0, (1.0, 0.15), '系统回复：冷提示')
place(paper(0.25, 1500, 5000), F(43.10), -8, 0.0, (0.6, 0.1), '补充材料框出现')
place(knock_note(m('C4'), 1.0), F(44.33), -5, -0.2, (1.0, 0.15), '卡片落进框')
place(beep(m('G5'), 0.10, 0.4), F(45.76), -8, 0.3, (1.0, 0.15), '上传完成')
place(beep(m('C6'), 0.16, 0.4), F(45.88), -8, 0.3, (1.0, 0.15), '上传完成')
place(click(), F(48.44), -7, 0.2, (0.5, 0.08), '点“展开”')
place(stamp([m('C3'), m('F#3')]), F(48.62), -6.5, 0.0, (2.0, 0.28), '原始内容已不可用')                  # 本章唯一的三全音闷击
for tc in (59.57, 60.27, 60.97):                                                                   # 生成光标亮（闪两下后停住）
    place(beep(m('C6'), 0.12, 0.3), F(tc), -10, 0.0, (1.0, 0.15), '光标')

# ---------- 输出 ----------
n = int(DUR * SR)
mix = out.x[:, :n].copy()
tt = np.arange(n) / SR
mix *= np.clip((TEND - tt) / 0.5, 0, 1)                      # 章末淡黑 421.17–421.67：声音一起收尽
mix[:, int(TEND * SR):] = 0
mix[:, :int(T0 * SR)] = 0

LOOPS = {'A': (F(0.45), F(11.49)), 'B': (TB0, TB0 + NB8 * E8), 'D': (TD0, TD0 + ND * S3), 'C': (TC0, TC0 + 12 * S3 + 1.0)}
print('--- 循环区间内的点缀（place 登记）---')
for nm, (a, b) in LOOPS.items():
    pts = sorted(t for t, rel, tag in LOG if a <= t <= b)
    close = [(x, y) for i, x in enumerate(pts) for y in pts[i + 1:] if y - x < 2.0]
    print(nm, (round(a, 2), round(b, 2)), 'n =', len(pts), pts, '2秒内成对:', close)
print('--- 全部点缀 ---')
for t, rel, tag in sorted(LOG): print(t, round(t - O, 2), rel, tag)
wavfile.write(__file__.replace('ch3.py', 'ch3-music.wav'), SR, mix.T.astype(np.float32))
pk = peaks_per_second(mix)
print('ok', round(n / SR, 2), 'peak', round(float(np.abs(mix).max()), 3))
print({i: p for i, p in enumerate(pk) if p > 0.001})
