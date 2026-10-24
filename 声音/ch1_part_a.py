"""第一章 122.85–155.17 秒声音点缀（协调者作曲）：后羿、嫦娥、风险台账。时间＝全片秒。
画面事件用 kit.frame_trace 在成片上核过：十个太阳 122.87 切入；127.4–129.9 九个太阳逐个熄灭（亮度台阶）；
“后羿 列入黑名单”标签 130.6 出现；儿童读物页 134.8、红印 135.1；138.07 切月夜；嫦娥旁代码约 139.9–143.5 逐字出现；
月球隔离圈 144.4–145.9 张开；月饼 148.7；风险台账“地区”红印 153.67；155.17 切“西方地区”（之后归子代理那段）。
设计：
- 十个太阳＝十个“生产实例”：一个由十个五声音阶正弦音组成的和弦，每个太阳一个音；每射落一个，就掐掉一个音，
  和弦一层层变薄，只剩最低的 D4 撑到切镜——射日这件事用和声本身来“讲”。
- 每一箭：弓弦“嘣”＋一个下行的小玻璃音（九个音依次往下）。
- 列入黑名单：闷击（三全音）。奉为英雄：三音小号角似的电钢琴。儿童读物：红印＋八音盒式的高音四下（讽刺）。
- 嫦娥：月夜一声空玻璃，代码逐字时的打字声，隔离圈张开时一个长长的空心低音＋一声“锁上”；
  “美化为神话”：月饼出来时一串甜过头的上行竖琴。
- 台账红印：闷击收在“记在了整个地区名下”。"""
import os, sys
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *

DUR = 158.0
out = Bus(DUR); place = make_place(out)

# ---------- 十个太阳的和弦，射一个少一个音 ----------
T_IN, T_CUT = 122.95, 131.9
shots = [127.45 + i * 0.295 for i in range(9)]
tones = ['B5', 'A5', 'F#5', 'E5', 'D5', 'B4', 'A4', 'F#4', 'E4', 'D4']   # 第 i 箭掐掉 tones[i]，D4 留到最后
suns = Bus(DUR)
for i, nm in enumerate(tones):
    end = shots[i] if i < 9 else T_CUT
    dur = end - T_IN + 0.08
    n = int(dur * SR); tt = np.arange(n) / SR; f = hz(m(nm))
    vib = 1 + 0.002 * np.sin(2 * np.pi * (4.5 + 0.3 * i) * tt + i)
    y = (np.sin(2 * np.pi * f * np.cumsum(vib) / SR) + 0.3 * np.sin(4 * np.pi * f * np.cumsum(vib) / SR))
    e = np.clip(tt / 1.6, 0, 1) * np.clip((dur - tt) / 0.06, 0, 1)            # 1.6 秒淡入；被射中 60ms 掐掉
    if i == 9: e = np.clip(tt / 1.6, 0, 1) * np.clip((dur - tt) / 0.8, 0, 1)
    suns.add(y * e, T_IN, 0.12, pan=-0.8 + 1.6 * ((i * 3) % 10) / 9)
out.x += level_bus(reverb(suns.x, 2.4, 0.35), 125, 127.3, -7)

place(beep(m('A6'), 0.05, 0.1), 127.33, -12, 0.3, (0.6, 0.1))                 # 瞄准圈出现
for i, t in enumerate(shots):                                                  # 九箭
    twang = pluck(m('D3'), 0.3, 0.95, 0.975)                                   # 弓弦
    place(twang, t - 0.03, -8, -0.5, (0.6, 0.08))
    place(glass(m(['B6', 'A6', 'F#6', 'E6', 'D6', 'B5', 'A5', 'F#5', 'E5'][i]), 1.2, 3.5, 1.6), t, -9, 0.2 + 0.05 * i, (1.4, 0.25))

place(stamp([m('D3'), m('G#3')]), 130.62, -3, -0.2, (1.8, 0.3))                # 列入黑名单
for i, nm in enumerate(['D4', 'A4', 'D5']):                                    # 奉为英雄：小号角
    place(ep(m(nm), 0.9 if i < 2 else 1.6), 132.25 + 0.2 * i, -6, 0.1, (1.6, 0.3))
place(paper(0.4, 800, 3500), 134.8, -6, 0, (0.8, 0.12))                        # 儿童读物翻出来
place(stamp([m('A3'), m('D4')]), 135.13, -3, 0.2, (1.4, 0.2))                  # 读物上的红印
for i, nm in enumerate(['D7', 'A6', 'F#6', 'A6']):                             # 八音盒四下
    place(glass(m(nm), 1.4, 5.0, 0.6), 135.7 + 0.22 * i, -9, 0.4, (1.6, 0.3))

# ---------- 嫦娥 ----------
place(glass(m('E5'), 4.0, 1.41, 0.6), 138.1, -8, -0.3, (3.0, 0.45))            # 月夜：一声空玻璃（“不止如此”）
ts = [139.9]
while ts[-1] < 143.5: ts.append(ts[-1] + 0.07 + 0.09 * rng.random())          # 代码逐字
for t in ts: place(tick(0.04, 2600 + 400 * rng.random()), t, -13, -0.4, (0.5, 0.08))
place(beep(m('E6'), 0.07, 0.4), 143.6, -9, -0.4, (0.8, 0.12))                  # 回车：访问到了
hol = Bus(DUR)                                                                 # 隔离圈张开：空心长音
hol.add(drone([m('A3'), m('E4')], 4.0, a=0.9, r=2.2, cutoff=900), 144.4, 1.0)
hol.add(glass(m('A4'), 4.0, 1.0, 0.5), 144.4, 0.6)
out.x += level_bus(reverb(hol.x, 3.2, 0.5), 144.6, 146.5, -6)
place(toggle(), 145.9, -6, 0.3, (1.2, 0.2)); place(beep(m('A4'), 0.18, 0.5), 146.0, -8, 0.3, (1.4, 0.25))   # 锁上
harp = [m(x) for x in ['D4', 'F#4', 'A4', 'D5', 'F#5', 'A5', 'D6', 'F#6', 'A6', 'D7']]                       # 美化为神话：甜过头的上行竖琴
for i, nt in enumerate(harp): place(pluck(nt, 1.6, 0.7, 0.997), 148.7 + 0.065 * i, -10, -0.6 + 0.13 * i, (2.2, 0.4))
place(glass(m('D7'), 2.0, 2.0, 0.4), 149.4, -10, 0.4, (2.4, 0.4))

# ---------- 风险台账 ----------
place(paper(0.45, 700, 3000), 151.1, -6, 0, (0.8, 0.12))
place(stamp([m('D3'), m('G#3')]), 153.67, -3, 0.1, (1.6, 0.25))                 # “记在了整个地区名下”

n = int(DUR * SR); mix = out.x[:, :n]
mix[:, :int(122.85 * SR)] = 0
wavfile.write(__file__.replace('ch1_part_a.py', 'ch1-part-a-music.wav'), SR, mix.T.astype(np.float32))
print('ok peak', round(float(np.abs(mix).max()), 3), 'peaks>1.2', [(i, v) for i, v in enumerate(peaks_per_second(mix)) if v > 1.2])
