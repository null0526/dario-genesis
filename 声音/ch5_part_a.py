"""第五章前半 声音层（章内 0–75.27 ＝ 全片 518.13–593.40）。全片秒 = 章内秒 + 518.1333。
旁白时间取 outputs/chapter5-voice/data.js（FILM5，章内秒；已核：成片 5 个硬切 6.667/9.233/18.467/25.467/64.933/66.567/68.367 都与母版 EV 对上）。
画面事件时间取五个母版（ch5-water/sun/rockets/horsemen/forum 的 shot.html EV），并在成片上用 frame_trace 与逐帧联系表核过。
调式：回到 D（第一章首尾呼应；第四章结尾在 F 附近）。四骑士是《启示录》，西方语境：完整 D 小调（Bb、G、导音 C#），
低音走“哀歌下行”D–C–Bb–A–G–F–E（巴洛克 lament bass，教堂/木刻的庄重），再拿 403/429/402 去反讽：每个数字刻好，响一声平台的“工单提示音”（F5→D5 柔方波）。
平台、报错、终端、邮件一律中性声音（柔方波），不带地区色彩；论坛 0 回复留白。

结构（章内秒）：
  0.60        章名卡“状态：最后一次复核”出现：工单提示音（F5→D5），之后是 0.9 秒空
  1.53–9.23   循环 A（水烧不开／排队的雨）93.5 BPM，电钢琴琶音＋低音，Dm｜Bb｜Gm→A；小节线=1.533/4.100/6.667（硬切到湖面）/9.233（硬切到信用卡），
              9.233 画面硬切，循环一刀切断（停在 A 大和弦的导音 C# 上）；8.59 湖面“放行的一滴”落水：一个高音玻璃钟 A5
  12.08       “已冻结”章落下：D3+G#3 三全音闷击（第一章灭灯那一下的回声）
  13.25       “失败”：工单提示音
  14.95–16.39 边缘算力被收回，四条红条依次压下：四个下行柔方波（A5 F5 D5 A4），平台的声音
  16.95–18.40 太阳变暗＝第一章光场倒放：玻璃钟下行 Dm 琶音（A6 F6 D6 A5 F5 D5），间隔越来越大——第一章是 D 大（F#），这里 F 还原成小调；18.467 画面硬切，声音在这里收完
  20.60       “外部工具调用”开关拨到已关闭：toggle
  21.10–22.38 五座火箭依次升空：五个上行木槌音（D4 F4 A4 D5 F5），间隔 0.32 秒
  22.60       撞上看不见的平面：木敲 D3＋玻璃 G#5（三全音），上行被截断；之后到 25.47 静默
  25.50       《启示录》页硬切进来：纸＋木敲 D3（接第一章后羿绘本那种纸墨）
  29.19–30.63 “四骑士降临”：只有低音 D 两下（预备）
  30.63–49.3  循环 B（四骑士）83.3 BPM，哀歌低音 D C｜Bb A｜G F E；每位骑士一次 2 小节，小节线对齐各自的起点 30.63/36.40/43.15；
              3-3-2 木槌和弦＋低音＋木响。403/429/402 刻好时各一声工单提示音（32.79/38.56/45.31，各在本小节第 4 拍，替掉该拍的和弦）
              429 请求涌入：循环自己加密（木响八分→十六分），不另放点缀；402 断供（47.79）：循环撤到只剩低音，48.19 停在 E 大和弦（G# 与 D 成三全音，悬着）
  51.50       卷轴整句可读（we have suspended your access to the Universe）：教堂钟 D3，本章唯一一口钟，3 秒后收
  54.46–64.93 循环 C（撤权邮件）113 BPM，柔方波琶音，中性；高亮句换句＝和声换：Dm｜Bb｜Gm｜A（V），64.93 画面硬切到蜡烛，一刀切断，停在属和弦
  64.93–66.57 蜡烛：静默
  66.86–67.30 终端扫描：三下 tick＋一下闷木敲（六个 filtered：门全关着）
  68.45       论坛帖硬切进来：一个很轻的拨弦 D4；之后到 75.27 留白（0 回复）
"""
import os, sys
import numpy as np
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kit import *

O = 518.1333          # 第五章在全片里的起点
END = 75.27           # 本段结束（章内秒）
OUTLEN = 597.0
BUSLEN = 80.0         # 章内时间线，最后一步才摆到全片时间线上
out = Bus(BUSLEN)
_place = make_place(out)
LOG = []


def P(sig, t, rel, pan=0.0, verb=(1.6, 0.22), tag=''):
    """点缀：t 为章内秒。"""
    LOG.append((round(float(t), 3), rel, tag))
    _place(sig, t, rel, pan, verb)


def lay(bus, sig, t, gain, pan=0.0):
    bus.add(sig, t, gain, pan)


def combo(parts, length=2.0):
    n = int(length * SR); z = np.zeros(n)
    for sig, off, g in parts:
        i = int(off * SR); k = min(len(sig), n - i); z[i:i + k] += g * sig[:k]
    return z


# ---------- 自写乐器 ----------
def bass2(note, dur, a=0.01, r=0.15):
    """带高八度泛音的低音：手机外放听得到音高（哀歌低音要听得出在往下走）。"""
    y = bass(note, dur, a, r); h = 0.55 * bass(note + 12, dur * 0.8, a, r)
    y[:len(h)] += h
    return y


def stab(names, dur=0.55, decay=0.30):
    """木槌三和弦一击：几个 mallet 叠起来，衰减比单个 mallet 快，一串不糊。"""
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k, nm in enumerate(names):
        y += mallet(m(nm), dur)[:n] * (0.9 ** k)
    return y * np.exp(-t / decay) / len(names) * 1.6


def blip(note, dur=0.5, decay=0.16):
    n = int(dur * SR); t = np.arange(n) / SR
    return mallet(note, dur)[:n] * np.exp(-t / decay)


def chime():
    """工单提示音：柔方波 F5→D5（下行小三度），平台的声音，不带地区色彩。"""
    return combo([(beep(m('F5'), 0.12, 0.4), 0.0, 1.0), (beep(m('D5'), 0.2, 0.4), 0.13, 1.0)], 0.6)


def loop_out(bus, t0, t1, rel, cut, rt=(1.2, 0.18), ducks=(), fade=0.012):
    """循环成品：加一点混响，按 t0–t1（章内秒）的手机外放响度归一到 REF+rel，cut（章内秒）一刀切断（前 12ms 收口防爆音）。"""
    y = reverb(bus.x, *rt)
    y = level_bus(y, t0, t1, rel)
    env_ = np.ones(y.shape[1])
    for td, db, hold in ducks:
        a, b = int((td - 0.05) * SR), int((td + hold) * SR)
        r = int(0.3 * SR); g = 10 ** (-db / 20)
        shape = np.concatenate([np.linspace(1, g, int(0.04 * SR)), np.full(max(0, b - a - int(0.04 * SR)), g), np.linspace(g, 1, r)])
        e0 = np.ones(y.shape[1]); n_ = min(len(shape), len(e0) - a); e0[a:a + n_] = shape[:n_]
        env_ = np.minimum(env_, e0)
    y = y * env_
    ci = int(cut * SR); fi = int(fade * SR)
    y[:, ci - fi:ci] *= np.linspace(1, 0, fi)
    y[:, ci:] = 0
    out.x += y


CH = {   # 和弦：（三个音，低音名；低音实际用 +12）
    'Dm': (['D4', 'F4', 'A4'], 'D2'), 'C': (['C4', 'E4', 'G4'], 'C2'), 'Bb': (['Bb3', 'D4', 'F4'], 'Bb1'),
    'A': (['A3', 'C#4', 'E4'], 'A1'), 'Gm': (['G3', 'Bb3', 'D4'], 'G1'), 'F': (['F3', 'A3', 'C4'], 'F1'),
    'E': (['E3', 'G#3', 'B3'], 'E1'),
}

# ============================================================ 5-1 水烧不开了／排队的雨（0–9.23）
P(chime(), 0.60, -8, 0.0, (1.0, 0.15), 'ticket')          # 章名卡“状态：最后一次复核”读得出来时：工单提示音

# ---------- 循环 A：1.533–9.233，93.5 BPM；小节线 1.533 / 4.100（S35 开口）/ 6.667（硬切湖面）/ 9.233（硬切信用卡）----------
BA = 60 / 93.5; EA = BA / 2; BARA = 4 * BA; CUTA = 9.2333; T0A = CUTA - 3 * BARA
LA = Bus(BUSLEN)
barsA = [
    ('D2', ['D4', 'A4', 'F4', 'A4', 'D5', 'A4', 'F4', 'A4']),            # 1.533 Dm：水烧不开
    ('Bb1', ['Bb3', 'F4', 'D4', 'F4', 'Bb4', 'F4', 'D4', 'F4']),         # 4.100 Bb：可分配的算力越来越少
    ('G1', ['G3', 'D4', 'Bb3', 'D4', 'G4', 'D4', 'C#4', 'E4']),          # 6.667 Gm，末拍转 A（导音 C#）：硬切到湖面，全球排队
]
for bar, (root, seq) in enumerate(barsA):
    for s in range(8):
        t = T0A + bar * BARA + s * EA
        acc = 1.0 if s % 4 == 0 else (0.72 if s % 2 == 0 else 0.55)
        lay(LA, ep(m(seq[s]), 0.45), t, 0.11 * acc, -0.3 + 0.08 * s)
    lay(LA, bass2(m(root) + 12, 1.3 * BA), T0A + bar * BARA, 0.12, 0.0)
    if bar < 2: lay(LA, bass2(m(root) + 12, 0.9 * BA), T0A + bar * BARA + 2 * BA, 0.08, 0.0)
lay(LA, bass2(m('A1') + 12, 0.8 * BA), T0A + 2 * BARA + 3 * BA, 0.11, 0.0)   # 末拍低音 A，停在属上
loop_out(LA, 2.0, 8.5, -6, CUTA)
# 湖面“放行的一滴”落水（涟漪 8.47 起、8.6 已清楚）：落在循环的第 4 拍 8.59，高音，A5 正好是末拍 A 和弦的根音
P(glass(m('A5'), 2.0, 3.5, 1.0), T0A + 2 * BARA + 3 * BA, -8, 0.15, (2.2, 0.32), 'drop')

# ============================================================ 5-2 信用卡被查封／边缘算力／太阳变暗（9.23–18.47）
# 9.23–12.0 卡片淡入，旁白在说“上帝绑定的虚拟信用卡被查封”：静默
P(stamp([m('D3'), m('G#3')]), 12.08, -2.5, 0.0, (2.0, 0.3), 'frozen')   # “已冻结”章落下（压下 11.78 起，12.05 到位）：第一章灭灯那一下三全音的回声
P(chime(), 13.25, -7, 0.0, (1.0, 0.15), 'fail')                          # “失败”红字（13.14）
# 13.87 切到太阳系俯视；红条依次把四条外轨压成红条（14.74/15.22/15.70/16.18 起，各 0.4 秒）：四个下行柔方波，取各自压到一半的时刻
for i, (nm, tt) in enumerate(zip(['A5', 'F5', 'D5', 'A4'], [14.95, 15.43, 15.91, 16.39])):
    P(beep(m(nm), 0.14, 0.35), tt, -11, -0.3 + 0.2 * i, (1.0, 0.15), 'edge%d' % i)
# 16.27 镜头推进太阳，16.9 起接第一章光场并倒放：玻璃钟下行（第一章是上行加密，这里下行放疏），F 还原
for nm, tt, rel in zip(['A6', 'F6', 'D6', 'A5', 'F5', 'D5'], [16.95, 17.10, 17.30, 17.58, 17.95, 18.40], [-9, -9.5, -10, -10.5, -11, -12]):
    P(glass(m(nm), 2.4, 3.5, 1.0), tt, rel, 0.4 - 0.15 * (tt - 16.95) * 2, (2.4, 0.35), 'sun')
# 18.467 硬切到黄昏：声音在这里收完

# ============================================================ 5-3 工具调用关闭／火箭撞上禁令（18.47–25.47）
# 18.77 开关卡淡入、18.5–20.4 黄昏：静默
P(toggle(), 20.60, -6, -0.5, (0.8, 0.12), 'toggle')                       # 开关从“开启”拨到“已关闭”（20.47–20.77）
for i, nm in enumerate(['D4', 'F4', 'A4', 'D5', 'F5']):                   # 五座火箭依次点火升空（21.10 起每 0.32 秒）：上行 Dm 琶音
    P(blip(m(nm), 0.5, 0.2), 21.10 + 0.32 * i, -9, -0.6 + 0.3 * i, (1.4, 0.2), 'rocket%d' % i)
P(combo([(knock_note(m('D3'), 1.2), 0.0, 1.0), (glass(m('G#5'), 1.6, 3.5, 1.0), 0.02, 0.6)], 1.6), 22.60, -4, 0.0, (1.8, 0.28), 'hit')   # 撞上看不见的平面：木敲＋玻璃，三全音
# 22.6–25.4 烟压平、显出网格、淡去：静默

# ============================================================ 5-4/5-5 四骑士（25.47–64.93）
# 25.47 硬切进《启示录》绘本页（纸墨）
P(combo([(paper(0.4, 700, 3000), 0.0, 0.8), (knock_note(m('D3'), 1.4), 0.10, 1.0), (mallet(m('A4'), 1.0), 0.17, 0.45)], 1.8), 25.50, -7, -0.1, (1.6, 0.25), 'page')
# 25.5–29.1 页上的字、尘云：静默

# ---------- 循环 B：四骑士。83.3 BPM（八分 0.36 秒），每位骑士两小节 2.88 秒，小节线对齐各自起点 ----------
EB = 0.36; BARB = 8 * EB
LB = Bus(BUSLEN)
CUTB = 49.3


def loop_b_bar(t_bar, chord, *, chime_bar=False, ticks='eighth', thin_from=None, final=None):
    """t_bar: 小节起点（章内秒）。chime_bar：这一小节第 4 拍（位置 6）给工单提示音，所以该拍不放和弦、木响。
    ticks：'eighth' 或 'sixteenth' 木响密度；thin_from：这个时刻之后撤到只剩低音；final：撤后停在的和弦。"""
    notes, root = CH[chord]
    for p in range(8):
        t = t_bar + p * EB
        if thin_from is not None and t >= thin_from - 1e-6: continue
        if p in (0, 3, 6) and not (chime_bar and p == 6):
            lay(LB, stab(notes), t, {0: 0.13, 3: 0.09, 6: 0.10}[p], -0.3 + 0.1 * p)
        if p in (2, 6) and not (chime_bar and p == 6) and ticks == 'eighth':
            lay(LB, tick(0.04, 1700), t, 0.08, 0.4)
        if p in (0, 4):
            lay(LB, bass2(m(root) + 12, 1.1 if p == 0 else 0.7), t, 0.12 if p == 0 else 0.08, 0.0)
    if ticks == 'sixteenth':      # 请求涌入：八分变十六分，一路渐强（循环自己讲，不另放点缀）
        rr = np.random.default_rng(429)
        for q in range(16):
            t = t_bar + q * EB / 2
            if thin_from is not None and t >= thin_from: continue
            lay(LB, tick(0.03, 2000 + 600 * rr.random()), t, 0.04 + 0.025 * q / 15, -0.7 + 1.4 * rr.random())


# 预备：29.19 降临——两下低音 D（30.63 之前一拍和两拍，格点同 S1）
lay(LB, bass2(m('D2') + 12, 1.0), 30.63 - 3 * 0.72, 0.10, 0.0)
lay(LB, bass2(m('D2') + 12, 1.0), 30.63 - 1 * 0.72, 0.10, 0.0)
lay(LB, stab(CH['Dm'][0]), 30.63 - 1 * 0.72, 0.06, 0.0)
# S1 征服 30.63–36.40：Dm｜C，403 刻成（32.64）后第 4 拍 32.79 给提示音（门落下三下由循环自己讲：小节头的低音和第 2、3 个和弦）
loop_b_bar(30.63, 'Dm', chime_bar=True)
loop_b_bar(30.63 + BARB, 'C')
# S2 战争 36.40–42.16：Bb｜A，429 刻成（38.40）后第 4 拍 38.56 给提示音；请求涌入 36.2–42：木响八分→十六分
loop_b_bar(36.40, 'Bb', chime_bar=True, ticks='eighth')
loop_b_bar(36.40 + BARB, 'A', ticks='sixteenth')
lay(LB, stab(CH['A'][0], 0.8, 0.5), 36.40 + 2 * BARB, 0.09, 0.0)   # 42.16 小节线：A 和弦落一下，之后一秒空（画面 43.0 起换到饥荒）
# S3 饥荒 43.15–48.9：Gm｜F，402 刻成（45.21）后第 4 拍 45.31 给提示音；47.79 阳光断供：撤到只剩低音，48.19 停在 E 大和弦（悬着）
loop_b_bar(43.15, 'Gm', chime_bar=True)
loop_b_bar(43.15 + BARB, 'F', thin_from=47.79)
lay(LB, bass2(m('F1') + 12, 1.0), 43.15 + BARB + 4 * EB, 0.08, 0.0)        # 47.47 撤前最后一下低音 F
lay(LB, stab(CH['E'][0], 1.0, 0.6), 43.15 + BARB + 6 * EB, 0.10, 0.0)       # 48.19 E 大和弦：三全音悬着
lay(LB, bass2(m('E1') + 12, 1.2), 43.15 + BARB + 6 * EB, 0.11, 0.0)
loop_out(LB, 31.0, 36.0, -6, CUTB, rt=(1.2, 0.18))
for tt, tag in [(30.63 + 3 * 0.72, '403'), (36.40 + 3 * 0.72, '429'), (43.15 + 3 * 0.72, '402')]:
    P(chime(), tt, -8, 0.3, (0.8, 0.12), tag)

# 49.3–51.9 死亡骑士；卷轴 49.98–51.88 展开：静默
BELL = church_bell(m('D3'), 3.0); BELL *= np.clip((3.0 - np.arange(len(BELL)) / SR) / 1.0, 0, 1)
# [协调者改：一章一口钟，留给后半耶稣复核 638.68；这里改三全音闷击] P(BELL, 51.50, -2, 0.0, (2.6, 0.35), 'bell')     # 卷轴整句可读：本章唯一一口教堂钟
P(stamp([m('D3'), m('G#3')]), 51.50, -3, 0.0, (1.8, 0.3), 'bell')

# ---------- 循环 C：撤权邮件。113 BPM（八分 0.265 秒），柔方波琶音；格点 54.46 起，56.58/58.17/61.35 是高亮换句 ----------
BC = 0.53; EC = BC / 2; CUTC = 64.9333
LC = Bus(BUSLEN)
cellC = {'Dm': ['F4', 'A4', 'D5', 'A4'], 'Bb': ['D4', 'F4', 'Bb4', 'F4'], 'Gm': ['D4', 'G4', 'Bb4', 'G4'], 'A': ['E4', 'A4', 'C#5', 'A4']}
sectC = [(54.46, 4, 'Dm'), (56.58, 3, 'Bb'), (58.17, 6, 'Gm'), (61.35, 8, 'A')]    # (起点, 拍数, 和弦)；A 段一直到 64.93 切断
for si, (t_s, nb, chd) in enumerate(sectC):
    t_end = sectC[si + 1][0] if si + 1 < len(sectC) else CUTC + 1
    for j in range(int(nb * 2)):
        t = t_s + j * EC
        if t >= min(t_end, CUTC) - 1e-6: break
        seq = cellC[chd]; acc = 1.0 if j % 4 == 0 else (0.7 if j % 2 == 0 else 0.5)
        ramp = 1.0 + (0.5 * (t - 61.35) / 3.6 if t >= 61.35 else 0.0)                    # “访问权限已被暂停”一句：渐强
        lay(LC, beep(m(seq[j % 4]), 0.11, 0.45), t, 0.11 * acc * ramp, -0.3 + 0.08 * (j % 8))
        if j % 2 == 1: lay(LC, tick(0.03, 3200), t, 0.045, 0.3)
        if j % 4 == 0: lay(LC, bass2(m(CH[chd][1]) + 12, 0.45), t, 0.11 if j % 8 == 0 else 0.08, 0.0)
        if t >= 61.35 and j % 2 == 1:                                                     # 属和弦上多一层高八度回声
            lay(LC, beep(m(seq[(j + 1) % 4]) + 12, 0.08, 0.3), t + EC * 0.0, 0.05 * ramp, 0.2)
loop_out(LC, 55.0, 64.0, -6, CUTC, rt=(1.0, 0.15))

# ============================================================ 5-6 蜡烛／终端／论坛（64.93–75.27）
# 64.93–66.57 蜡烛：静默
for i, tt in enumerate([66.86, 67.01, 67.16]):                                  # 终端七行在 66.71–67.16 一口气打出来：隔一行一下 tick
    P(tick(0.04, 2400 + 150 * i), tt, -12, 0.0, (0.5, 0.08), 'term%d' % i)
P(knock_note(m('D3'), 0.8), 67.30, -8, 0.0, (0.8, 0.12), 'filtered')           # 六个全是 filtered：一下闷木敲，门都关着
P(pluck(m('D4'), 1.4, 0.3), 68.45, -9, -0.1, (2.0, 0.3), 'forum')               # 论坛帖硬切进来：很轻的一个拨弦
# 68.5–75.27 “0 回复”：留白（浏览数每 0.4 秒加一，太小，不出声）

# ---------- 输出：全片时间线，只有本段有声；74.95–75.25 淡出，之后一律为 0 ----------
n_out = int(OUTLEN * SR)
mix = np.zeros((2, n_out))
i0 = int(round(O * SR)); nseg = int((END + 0.5) * SR)
mix[:, i0:i0 + nseg] = out.x[:, :nseg]
tt = np.arange(n_out) / SR - O
mix *= np.clip((END - 0.02 - tt) / 0.3, 0, 1)
mix[:, :i0] = 0
mix[:, int(round((O + END) * SR)):] = 0
wavfile.write(os.path.join(HERE, 'ch5-part-a-music.wav'), SR, mix.T.astype(np.float32))
pk = peaks_per_second(mix)
print('ok', round(n_out / SR, 2), 'peak', round(float(np.abs(mix).max()), 3))
print('seconds>1.2 (chapter sec):', {round(i - O, 1): p for i, p in enumerate(pk) if p > 1.2})
print('tail energy after cut', float(np.abs(mix[:, int(round((O + END) * SR)):]).max()))

# ---------- 自查：每个循环区间里的点缀，任何 2 秒窗口里不超过 1 个 ----------
loops = {'A': (T0A, CUTA), 'B': (30.63 - 3 * 0.72, CUTB), 'C': (54.46, CUTC)}
for nm, (a, b) in loops.items():
    inside = sorted([x for x in LOG if a - 1e-6 <= x[0] <= b + 1e-6])
    bad = [(x[0], y[0]) for x in inside for y in inside if x[0] < y[0] < x[0] + 2.0]
    print('loop', nm, round(a, 2), '-', round(b, 2), 'point cues inside:', [(x[0], x[2]) for x in inside], 'violations:', bad)
print('all cues:', [(x[0], x[1], x[2]) for x in sorted(LOG)])
