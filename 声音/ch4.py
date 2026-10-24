"""第四章 声音层：循环垫底＋少量点缀（Claude 子代理，10/22）。全片 421.87–517.93 秒；全片秒 = 章内秒 + 421.8667。
调式 F。东方（地球上的中国用户、风险台账）用 F 五声（F G A C D）；平台/风控是中性柔方波；星际部分用完整 F 大调（含 E 导音、Bb 四级）。
所有时间都用“章内秒”写（和 outputs/chapter4-voice/data.js 的 FILM4 同一把尺），最后整体放到全片时间线上。
画面事件时间：旁白锚点读 data.js（和各母版的 phraseT 同一算法），再用 kit.frame_trace 在 全片-r3.mp4 上核过
  （切镜 6.70/12.87/28.07/34.37/38.60/59.07/77.07/90.67；封号光轨被拉直 17.37–17.85；灭灯 19.70；气泡 26.2–26.4；
    光束出现 31.60；爆闪 70.95–71.0；通知卡 71.7；煤落地 75.6；翻页 91.97–93.38；淡黑 95.57–96.07）。

结构（先分段：稳定段给循环，转折点给一次性重拍或留白）：
  0.42–12.87   ★循环 1（行星掉电→二手平台）  F 大调 96 BPM：低音＋木槌分解和弦（4-1 只走四分音，6.64 切到二手页后加密到八分＋hat＋电钢琴高音）；
               12.87 硬切到拼车时一刀切断（和画面硬切同一帧）
  13.23–17.32  ★循环 2（拼车：47 条光轨依次伸出）  117 BPM 拨弦，随光轨涌入逐层加声部；17.32 光轨被拉直＝磁带停转（tapestop）
  19.72        灭灯：三全音闷击（F–B）
  21.6–24.0    风控虚线圈“？”跳 10 下 → 每隔一下一个冷提示（共 5 个，极轻）
  26.25        群聊气泡“别急，正在申诉”：在死寂里一个欢快的两音提示
  28.41–34.35  ★循环 3（深空天线齐转向黑洞）  81 BPM 柔方波琶音；31.57 光束出现＝循环里多一个高八度和弦；34.35 硬切到星图时一刀切断
  34.95        星图中央那片星褪掉：一个玻璃音
  36.35        “大过滤器”：教堂钟（本章只此一口）
  39.09–50.94  ★循环 4（地球·按地区分配）  F 五声 101 BPM：低音＋拨弦＋hat；扫描线＝拨弦音型上行一遍；4 个跳点＝高音点；
               5 项勾选＝拨弦五个上行音；50.94 “名单内外”一刀切断
  54.17/55.52/57.04  三处亮起（聚变装置/数据中心/发射场）：木槌 F–A–C 上行（无循环）
  59.42–70.93  ★循环 5（核聚变：点火→护栏→切断→失控）  104 BPM：点火是上行琶音；61.72 护栏框锁住＝转 d 小调加冷提示；
               66.9–69.5 十二条磁力线逐根熄灭＝琶音一格格被拿掉；69.63 起低音加速、升调；70.93 一刀切断
  70.95        爆闪：重拍（F–Gb 小二度簇）
  71.72        系统通知卡：两音礼貌提示
  75.62        煤落地：低木头敲击（无循环）
  77.5–82.49   ★循环 6（火星→请求飞向 api）  d 小调低音区，79.27 起飞：升八度、换 Bb、速度越来越快；82.49 一刀切断
  82.65        Unsupported Region：两声冷提示（F5→B4 下行三全音）
  86.55/89.50  罪证纸条滑入：纸声；纸条写完：闷击（F–C 纯五度）
  91.0–93.4    ★循环 7（台账翻页加速）  低音脉冲＋木槌下行音阶，音跟着 10 次翻页越来越密
  93.42/94.85  Bb（IV）→ F（I）阿们终止，随 95.57–96.07 淡黑收尽（本章唯一一次）"""
import os
import sys
import json
import numpy as np
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from kit import *   # noqa

OFF = 421.86667            # 第四章零点在全片里的秒数（timeline.json 的 r4e）
TEND = 96.06667            # 章末（517.93）
DURC = 97.0                # 章内总线时长
FULL = 521.0               # 输出 wav 长度
R = np.random.default_rng(20261024)

# ---------- 旁白锚点（和母版的 phraseT 同一算法）----------
_s = open(os.path.join(HERE, '..', '数据', 'ch4.js'), encoding='utf8').read()
FILM4 = json.loads(_s[_s.index('=') + 1:].strip().rstrip(';'))


def PT(pid, s, k=0):
    p = [p for p in FILM4['parts'] if p['id'] == pid][0]
    return p['charTimes'][p['text'].index(s) + k]


out = Bus(DURC)
_place = make_place(out)
LOG = []        # 点缀登记（place 调用）
ACC = []        # 并入循环的重音登记（循环自己的音，不算独立点缀，但也列出来核密度）


def place(sig, t, rel=0.0, pan=0.0, verb=(1.6, 0.22)):
    LOG.append((round(float(t), 2), rel))
    return _place(sig, t, rel, pan, verb)


def ease(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def cutoff(x, t_cut, fade=0.012):
    """一刀切断：t_cut 起 fade 秒淡出，之后全零。"""
    i = int(t_cut * SR); n = int(fade * SR)
    y = x.copy(); y[:, i:i + n] *= np.linspace(1, 0, n); y[:, i + n:] = 0
    return y


def snap(t, t0, grid):
    return t0 + round((t - t0) / grid) * grid


# ---------- 自写小乐器 ----------
def blip(note, dur=0.5, decay=0.16):
    """短木槌音：衰减比 mallet 快得多，循环里一串八分音不糊。"""
    n = int(dur * SR); t = np.arange(n) / SR
    return mallet(note, dur)[:n] * np.exp(-t / decay)


PAT = [0, 1, 2, 3, 2, 1, 2, 1]

# ================= 4-1 / 4-2 循环 1：0.42–12.87，F 大调，96.4 BPM（一小节 2.49 秒，正好五小节） =================
T1a, B1, N1 = 0.42, 2.49, 5
E1 = B1 / 8
CH1 = [('F2', ['F4', 'A4', 'C5', 'F5']), ('D2', ['F4', 'A4', 'D5', 'F5']), ('Bb1', ['F4', 'Bb4', 'D5', 'F5']),
       ('C2', ['G4', 'C5', 'E5', 'G5']), ('Bb1', ['F4', 'Bb4', 'D5', 'F5'])]
MARKET = snap(6.70, T1a, E1)     # 6.70 硬切到二手页 → 吸附到八分格 6.64
L1 = Bus(DURC)
for k in range(N1 * 8):
    t = T1a + k * E1; bar, pos = divmod(k, 8)
    root, tones = CH1[bar]
    mk = t >= MARKET - 1e-6
    if pos in (0, 4):
        L1.add(bass(m(root) + 12, 1.1), t, 0.12)
    if mk or pos % 2 == 0:                                   # 4-1 只走四分音；二手页起加密到八分
        L1.add(blip(m(tones[PAT[pos]]), 0.5, 0.17), t, 0.2, -0.3 + 0.6 * pos / 7)
    if mk and pos % 2 == 1:
        L1.add(hat(), t, 0.05, 0.25)
    if mk and pos == 0 and bar >= 3:
        L1.add(ep(m(tones[3]), 1.6), t, 0.085, 0.3)           # 二手页稳定后，电钢琴高音垫一下
    if bar == 3 and pos == 7:
        L1.add(blip(m('C6'), 0.5, 0.2), t, 0.12, 0.35)         # 换尾音
L1.add(ep(m('F6'), 1.4), MARKET, 0.11, 0.3)                    # 6.64 切到二手页：电钢琴一个高音（并进循环）
ACC.append(('循环1', MARKET, '二手页出现：电钢琴 F6'))
l1 = reverb(L1.x, 1.2, 0.18)
l1 = cutoff(level_bus(l1, 7.0, 12.0, -6.5), 12.87)            # 12.87 硬切到拼车：一刀切断
out.x += l1

# ================= 4-3 循环 2：13.23–17.32，拼车（117.4 BPM，两小节），17.32 磁带停转 =================
T2a, T2b = 13.23, 17.32
B2 = (T2b - T2a) / 2; E2 = B2 / 8
CH2 = [('F2', ['F4', 'A4', 'C5', 'F5']), ('Bb1', ['F4', 'Bb4', 'D5', 'F5']), ('C2', ['G4', 'C5', 'E5', 'G5'])]
PAT2 = [0, 1, 2, 3, 2, 1, 2, 3]
L2 = Bus(DURC)
for k in range(24):
    t = T2a + k * E2; bar, pos = divmod(k, 8)
    root, tones = CH2[bar]
    if t > T2b + 0.7: break
    if pos in (0, 4):
        L2.add(bass(m(root) + 12, 0.9), t, 0.12)
    if t >= 13.45:                                           # 第一批光轨伸出：拨弦琶音进来
        L2.add(pluck(m(tones[PAT2[pos]]), 0.7, 0.55, 0.992), t, 0.2, -0.4 + 0.8 * pos / 7)
    if t >= 14.0 and pos % 2 == 1:
        L2.add(hat(), t, 0.05, 0.25)
    if t >= 14.5:                                            # 车位计数涨起来：高八度回声加密
        g = 0.07 + 0.07 * ease((t - 14.5) / 1.0)
        L2.add(pluck(m(tones[PAT2[(pos + 3) % 8]]) + 12, 0.35, 0.6, 0.99), t + E2 / 2, g, 0.4 - 0.8 * pos / 7)
l2 = reverb(L2.x, 1.2, 0.18)
l2 = level_bus(l2, 15.5, 17.2, -6)
l2 = tapestop(l2, T2b, 0.55)                                 # 17.32 “共享账号被封”：光轨被拉直，循环磁带停转
out.x += l2

# ================= 4-3 后半：灭灯、风控找人、气泡（循环已停，静默里只留几个点） =================
place(stamp([m('F3'), m('B3')]), 19.72, -1, 0.0, (2.2, 0.3))                                      # 19.70 全车灯同一帧熄灭：三全音闷击
HOPS0 = PT('S25', '没人知道'); HOPD = ((PT('S25', '车主') - 0.25) - HOPS0) / 10                   # 风控圈十次跳，每跳 0.30 秒
for j, (k, nm) in enumerate(zip([0, 2, 4, 6, 8], ['C6', 'A5', 'E6', 'F#5', 'B5'])):                # 每隔一下出一个冷提示，极轻、中性
    place(beep(m(nm), 0.07, 0.4), HOPS0 + HOPD * k + 0.08, -13.5, [-0.4, 0.3, -0.2, 0.4, 0.0][j], (0.6, 0.1))
place(blip(m('C6'), 0.6, 0.22), 26.25, -5, 0.2, (1.2, 0.2))                                # 26.2 气泡弹出：群聊提示两音，欢快
place(blip(m('F6'), 0.7, 0.26), 26.36, -5, 0.2, (1.2, 0.2))

# ================= 4-4 循环 3：28.41–34.35，天线齐转向黑洞（81 BPM，两小节），34.35 一刀切断 =================
T3a = 28.41; B3 = (34.35 - 28.41) / 2; E3 = B3 / 8
CH3 = [('F2', ['F4', 'A4', 'C5', 'E5']), ('Bb1', ['F4', 'Bb4', 'D5', 'F5'])]
BEAM = snap(31.60, 31.38, E3 / 2)                           # 31.60 光束出现 → 吸附到十六分格
BEAM_END = 33.93
L3 = Bus(DURC)
for k in range(16):
    t = T3a + k * E3; bar, pos = divmod(k, 8)
    root, tones = CH3[bar]
    if pos in (0, 4):
        L3.add(bass(m(root) + 12, 1.3), t, 0.12)
    L3.add(beep(m(tones[PAT[pos]]), 0.09, 0.4), t, 0.3, -0.3 + 0.6 * pos / 7)
    if BEAM <= t + E3 / 2 < BEAM_END and pos % 2 == 1:      # 光束在时：高八度回声
        L3.add(beep(m(tones[PAT[pos]]) + 12, 0.07, 0.4), t, 0.14, 0.4 - 0.8 * pos / 7)
for nm, g in [('C6', 0.2), ('F6', 0.2), ('A6', 0.14)]:
    L3.add(beep(m(nm), 0.4, 0.4), BEAM, g, 0.0)             # 光束出现：高八度和弦（并进循环）
ACC.append(('循环3', BEAM, '光束出现：高八度 F 和弦'))
l3 = reverb(L3.x, 1.0, 0.15)
l3 = cutoff(level_bus(l3, 29.2, 31.3, -6), 34.35)
out.x += l3

place(glass(m('A5'), 2.4, 3.5, 0.8), 34.95, -9, -0.2, (2.4, 0.35))                               # 34.8–35.3 星图中央那片星褪掉
place(church_bell(m('F3'), 4.6), 36.35, -3, 0.0, (2.8, 0.4))                                       # 36.3 “这就是大过滤器”：本章唯一一口钟

# ================= 4-5 循环 4：39.09–50.94，地球·按地区分配（F 五声，101 BPM，五小节） =================
T4a, B4, N4 = 39.09, 2.37, 5
E4 = B4 / 8; S4 = E4 / 2
ROOT4 = ['F2', 'F2', 'D2', 'C2', 'F2']
PL4 = [['F4', 'A4', 'C5', 'A4', 'D5', 'C5', 'A4', 'G4'],
       ['F4', 'G4', 'A4', 'C5', 'F4', 'G4', 'A4', 'C5'],       # 后半 42.64 起＝扫描线开始，拨弦上行
       ['D5', 'F5', 'G5', 'A5', 'C5', 'A4', 'G4', 'A4'],       # 前半把上行音型走完（扫描线 42.6–44.4）
       ['C5', 'A4', 'G4', 'A4', 'C5', 'D5', 'C5', 'A4'],
       [None, None, None, None, None, 'C5', 'A4', 'F4']]       # 前半留给五个勾选的上行音
HOPT = [PT('S28', '中国用户') + 0.45 + 0.9625 * i for i in range(1, 5)]  # 路线四个跳点（ROUTE_T0=cn+0.45，每段 0.96 秒）
FAKE = PT('S28', '努力伪装')
TICKS = [snap(FAKE + 0.25 + 0.38 * i, T4a, S4) for i in range(5)]                                   # 五项勾选
L4 = Bus(DURC)
for k in range(N4 * 8):
    t = T4a + k * E4; bar, pos = divmod(k, 8)
    if pos in (0, 4):
        L4.add(bass(m(ROOT4[bar]) + 12, 1.1), t, 0.12)
    nm = PL4[bar][pos]
    if bar == 3 and pos == 7: nm = None                        # 给勾选的第一个音让位
    if nm: L4.add(pluck(m(nm), 0.9, 0.6, 0.994), t, 0.2, -0.4 + 0.8 * pos / 7)
    if bar >= 2 and pos % 2 == 1:
        L4.add(hat(), t, 0.04, 0.25)
for i, th in enumerate(HOPT):                                                                       # 跳点：高音点（循环里的重音）
    ts = snap(th, T4a, S4)
    L4.add(blip(m('F6'), 0.6, 0.2), ts, 0.2, 0.4 - 0.25 * i)
    ACC.append(('循环4', round(ts, 2), f'路线跳点{i+1}：F6'))
for i, (ts, nm) in enumerate(zip(TICKS, ['F5', 'G5', 'A5', 'C6', 'D6'])):                            # 勾选：五个上行拨弦音（循环自己的音型）
    L4.add(pluck(m(nm), 0.7, 0.65, 0.992), ts, 0.22, -0.3 + 0.15 * i)
    ACC.append(('循环4', round(ts, 2), f'勾选{i+1}：{nm}'))
l4 = reverb(L4.x, 1.2, 0.18)
l4 = cutoff(level_bus(l4, 41.0, 46.0, -6.5), 50.94)         # 50.95 “名单内外”：一刀切断
out.x += l4

for t0_, nm, rel in [(PT('S30', '自己造能源') + 0.12, 'F5', -6), (PT('S30', '自己训练') + 0.12, 'A5', -6), (PT('S30', '最好还能') + 0.12, 'C6', -5)]:
    place(blip(m(nm), 1.0, 0.45), t0_, rel, 0.0, (1.8, 0.28))                                       # 三处亮起：木槌 F–A–C 上行

# ================= 4-6 循环 5：59.42–70.93，核聚变（104 BPM，五小节，正好落在爆闪上） =================
T5a, B5, N5 = 59.42, (70.93 - 59.42) / 5, 5
E5 = B5 / 8
GUARD = PT('S31', '安全护栏'); CUT = PT('S31', '它切断'); LOSE = PT('S31', '等离子体')
CUTS = [CUT + 0.35 + (LOSE - 0.15 - CUT - 0.35) * k / 11 for k in range(12)]
CH5 = [('F2', ['F4', 'A4', 'C5', 'F5']), ('D2', ['D4', 'F4', 'A4', 'D5']), ('Bb1', ['F4', 'Bb4', 'D5', 'F5']),
       ('G2', ['G4', 'Bb4', 'D5', 'G5']), ('C2', ['G4', 'C5', 'E5', 'G5'])]
UP = ['F4', 'A4', 'C5', 'F5', 'A5', 'C6', 'F6', 'A6']         # 点火：整小节一路上行
ORDER = list(R.permutation(8))                                 # 十二根磁力线熄灭时，琶音的八个位置按这个顺序被拿掉
L5 = Bus(DURC)
for k in range(N5 * 8):
    t = T5a + k * E5; bar, pos = divmod(k, 8)
    root, tones = CH5[bar]
    if t >= LOSE - 1e-6: break                                 # 69.63 起交给加速低音
    if bar == 0:
        L5.add(blip(m(UP[pos]), 0.5, 0.17), t, 0.1 + 0.12 * pos / 7, -0.4 + 0.8 * pos / 7)
    else:
        nc = sum(1 for c in CUTS if t > c)
        removed = int(round(nc * 8 / 12))
        if ORDER.index(pos) >= removed:
            L5.add(blip(m(tones[PAT[pos]]), 0.5, 0.17), t, 0.2, -0.4 + 0.8 * pos / 7)
    if (bar == 0 and pos % 2 == 0) or bar >= 1:
        L5.add(bass(m(root) + 12, 0.2), t, 0.10 if bar else 0.08)
    if t >= GUARD - 0.02 and pos in (0, 4):
        L5.add(beep(m('C6'), 0.07, 0.4), t, 0.16, 0.0)           # 61.72 护栏框锁住：循环里加一个冷提示声部
        L5.add(beep(m('E6') if bar % 2 else m('B5'), 0.07, 0.4), t + E5 / 2, 0.10, 0.2)
ACC.append(('循环5', round(GUARD, 2), '护栏锁住：循环转 d 小调＋冷提示声部'))
for c in CUTS: ACC.append(('循环5', round(c, 2), '一根磁力线熄灭：琶音少一格'))
t, kk = LOSE, 0                                                # 失控：低音加速、升调，直到爆闪
while t < 70.93 - 0.01:
    u = ease((t - LOSE) / 1.2); iv = E5 / (1 + 7 * u)
    L5.add(bass(m('F2') + 12 + int(6 * ease((t - LOSE) / 1.3)), min(0.25, iv * 2)), t, 0.10 + 0.10 * u)
    t += iv; kk += 1
l5 = reverb(L5.x, 1.0, 0.15)
l5 = cutoff(level_bus(l5, 62.0, 66.0, -5.5), 70.93)           # 70.93 爆闪：一刀切断
out.x += l5

place(stamp([m('F3'), m('Gb3')]), 70.95, -3, 0.0, (2.4, 0.3))                                       # 爆闪：小二度簇，重拍
place(beep(m('C6'), 0.1, 0.35), 71.72, -7, 0.1, (1.0, 0.15))                                       # 系统通知卡滑入：礼貌的两音
place(beep(m('F6'), 0.16, 0.35), 71.86, -7, 0.1, (1.0, 0.15))
place(knock_note(m('F2'), 1.6), 75.62, -3, 0.0, (1.6, 0.2))                                        # 煤落进环中央

# ================= 4-7 循环 6：77.5–82.49，火星→请求飞向 api（d 小调低音区，越走越快） =================
LAUNCH = PT('S32', '发出第一条请求') - 0.5 + 0.5; ARRIVE = PT('S32', 'Unsupported') - 0.12
L6 = Bus(DURC)
t, kk = 77.5, 0
while t < ARRIVE - 0.01:
    pos = kk % 4; post = t >= LAUNCH - 1e-6
    sp = 1 + 1.2 * ease((t - LAUNCH) / 3.0)
    root = 'Bb1' if post else 'D2'
    tones = ['F4', 'Bb4', 'D5', 'F5'] if post else ['D3', 'F3', 'A3', 'D4']
    if pos == 0 or (post and pos == 2):
        L6.add(bass(m(root) + 12, 0.7 / sp), t, 0.12)
    L6.add(blip(m(tones[PAT[pos]]), 0.5, 0.2 / sp ** 0.5 if post else 0.28), t, 0.2, -0.3 + 0.2 * pos)
    t += 0.5 / sp; kk += 1
L6.add(blip(m('A5'), 0.9, 0.3), LAUNCH, 0.26, 0.2)               # 79.27 起飞的闪光（并进循环）
ACC.append(('循环6', round(LAUNCH, 2), '起飞闪光：A5，循环升八度换 Bb'))
l6 = reverb(L6.x, 1.0, 0.15)
l6 = cutoff(level_bus(l6, 77.6, 82.0, -7), ARRIVE)             # 82.49 到达 api 门：一刀切断
out.x += l6

UNS = PT('S32', 'Unsupported')
place(beep(m('F5'), 0.14, 0.4), UNS + 0.05, -6, 0.3, (1.0, 0.15))                                   # Unsupported Region：两声冷提示，下行三全音
place(beep(m('B4'), 0.34, 0.4), UNS + 0.22, -6, 0.3, (1.2, 0.18))
place(paper(0.4), PT('S32', '风险罪证') + 0.12, -7, 0.3, (0.6, 0.1))                                # 罪证纸条滑入
place(stamp([m('F3'), m('C4')]), PT('S32', '试图跨区') + 0.9, -3, 0.0, (1.8, 0.25))                  # 纸条写完：闷击（纯五度，不用三全音）

# ================= 4-8 循环 7：台账翻页加速（91.0–93.4）与阿们终止 =================
FL = [92.03, 92.33, 92.57, 92.78, 92.92, 93.05, 93.14, 93.20, 93.26, 93.32]   # 十次翻页（frame_trace 在台账区域上读出），越翻越快
FN = ['F6', 'E6', 'D6', 'C6', 'Bb5', 'A5', 'G5', 'F5', 'E5', 'D5']             # 下行 F 大调音阶：回到过去
L7 = Bus(DURC)
for tb in [91.05, 91.55]:
    L7.add(bass(m('F2') + 12, 0.5), tb, 0.12)
for i, (tf, nm) in enumerate(zip(FL, FN)):
    L7.add(blip(m(nm), 0.4, 0.14), tf, 0.2 + 0.02 * i, 0.4 - 0.08 * i)
    if i % 2 == 0: L7.add(bass(m('F2') + 12, 0.35), tf, 0.10)
l7 = reverb(L7.x, 1.0, 0.15)
l7 = cutoff(level_bus(l7, 91.9, 93.4, -6), 93.40, 0.02)       # 停在伊甸园那页
out.x += l7
PAGE_END = 93.40
place(pad([m('Bb2'), m('F3'), m('Bb3'), m('D4'), m('F4')], 1.5, a=0.08, r=0.9, cutoff=1100, cutoff_end=2800), PAGE_END + 0.02, -6.5, 0, (2.6, 0.4))     # IV
place(pad([m('F2'), m('C3'), m('F3'), m('A3'), m('C4')], 3.3, a=0.10, r=2.0, cutoff=1100, cutoff_end=3000), 94.85, -5, 0, (2.8, 0.4))                    # I：旁白读完，阿们
place(glass(m('F5'), 2.4, 3.5, 1.0) + 0.6 * glass(m('A5'), 2.4, 3.5, 1.0), 94.85, -9, 0.1, (2.4, 0.35))

# ---------- 输出：整章时间线 ----------
nloc = int(TEND * SR)
mix = out.x[:, :nloc].copy()
tt = np.arange(nloc) / SR
mix *= np.clip(tt / 0.35, 0, 1)                                   # 章首 0.35 秒淡入
mix *= np.clip((TEND - tt) / 0.5, 0, 1)                           # 章末淡黑 517.43–517.93：声音一起收尽
full = np.zeros((2, int(FULL * SR)))
i0 = int(round(OFF * SR)); full[:, i0:i0 + nloc] = mix
wavfile.write(os.path.join(HERE, 'ch4-music.wav'), SR, full.T.astype(np.float32))

LOOPS = {'1': (T1a, 12.87), '2': (T2a, T2b), '3': (T3a, 34.35), '4': (T4a, 50.94), '5': (T5a, 70.93), '6': (77.5, ARRIVE), '7': (91.0, PAGE_END)}
print('--- 循环区间内的点缀（place 登记；章内秒）---')
for nm, (a, b) in LOOPS.items():
    pts = sorted(t for t, rel in LOG if a <= t <= b)
    close = [(x, y) for i, x in enumerate(pts) for y in pts[i + 1:] if y - x < 2.0]
    acc = sorted(t for n_, t, _ in ACC if n_ == '循环' + nm)
    cl2 = [(x, y) for i, x in enumerate(acc) for y in acc[i + 1:] if y - x < 2.0]
    print(f'循环{nm}', (round(a, 2), round(b, 2)), 'place点缀 n =', len(pts), pts, '2秒内成对:', close, '| 并入循环的重音', len(acc), '2秒内成对:', len(cl2))
print('--- 全部点缀（place）---')
for t, rel in sorted(LOG): print(f'{t:6.2f} (全片 {t + OFF:7.2f})  rel {rel}')
pk = peaks_per_second(full)
print('ok', round(full.shape[1] / SR, 2), 'peak', round(float(np.abs(full).max()), 3))
print({i: p for i, p in enumerate(pk) if p > 0.001})
print('loop starts / ends 全片秒:', {k: (round(a + OFF, 2), round(b + OFF, 2)) for k, (a, b) in LOOPS.items()})
