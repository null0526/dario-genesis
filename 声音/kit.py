"""声音点缀的公共工具（协调者 Claude 整理，10/22）。各段作曲脚本 from kit import * 即可。
- 电平：每个点缀单独按“手机外放”口径归一（300Hz 四阶高通、100ms 窗能量峰值），基准 REF=-20 dBFS；
  样片混音时 REF 对齐到旁白同口径 90 分位下 2 dB（见 mix_sample.py）。所以 rel=0 ≈ 比旁白低 2 dB。
- 画面事件：frame_trace() 从成片裁一块区域，返回逐帧亮度或逐帧变化量，用来找点击、开关、灭灯、切镜的准确时刻。"""
import os
import subprocess
import numpy as np
from synth import *   # noqa: F401,F403  乐器与 Bus、reverb、hp/lp/bp 等

REF = -20.0
FILM = os.environ.get('DARIO_FILM', 'film.mp4')   # 成片路径，只有 frame_trace 用到；用环境变量 DARIO_FILM 指定


def phone_level(x, win=0.1):
    """“手机外放”响度：300Hz 四阶高通后，win 秒滑窗能量的峰值（dBFS）。"""
    y = hp(x.mean(axis=0) if x.ndim == 2 else x, 300, 4)
    w = int(win * SR)
    if len(y) < w: y = np.pad(y, (0, w - len(y)))
    c = np.concatenate([[0], np.cumsum(y ** 2)]); e = (c[w:] - c[:-w]) / w
    return 10 * np.log10(e.max() + 1e-12)


def stereo(sig, pan=0.0):
    if sig.ndim == 2: return sig
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    return np.vstack([sig * l * 1.414, sig * r * 1.414])


def make_place(out):
    """返回 place(sig, t, rel, pan, verb)：单个点缀先加混响，再按 100ms 手机外放响度归一到 REF+rel，加到 out。"""
    def place(sig, t, rel=0.0, pan=0.0, verb=(1.6, 0.22)):
        sig = hp(stereo(sig, pan), 75)        # 75Hz 以下扬声器放不出，只会让峰值虚高
        if verb: sig = reverb(np.hstack([sig, np.zeros((2, int(verb[0] * 1.3 * SR)))]), *verb)
        out.add(sig * 10 ** ((REF + rel - phone_level(sig, 0.1)) / 20), t)
    return place


def level_bus(x, t0, t1, rel):
    """持续的段落（循环、垫音）：按 t0–t1 这一段的 400ms 手机外放峰值归一到 REF+rel。"""
    return x * 10 ** ((REF + rel - phone_level(x[:, int(t0 * SR):int(t1 * SR)], 0.4)) / 20)


def knock_note(note, dur=1.4):
    """带音高的木头敲击（中频有“咚”，扬声器听得见）。"""
    n = int(dur * SR); t = np.arange(n) / SR
    y = mallet(note, dur) + 0.5 * mallet(note + 12, dur) * np.exp(-t / 0.3)
    k = int(0.03 * SR)
    y[:k] += bp(rng.uniform(-1, 1, k), 800, 2500) * np.exp(-np.arange(k) / SR / 0.006) * 0.6
    return y


def stamp(tone):
    """盖章/重拍：中频木头“咚”＋低频垫底＋两个带音高的木槌。tone 例：[m('D4'), m('F4')]。"""
    y = thud(0.7, 90, tone); n = len(y); t = np.arange(n) / SR
    return y + 0.9 * bp(rng.uniform(-1, 1, n), 250, 900) * np.exp(-t / 0.035)


def frame_trace(t0, dur, crop=None, mode='diff', film=FILM):
    """从成片取 t0 起 dur 秒、crop='w:h:x:y'（1920x1080 坐标）区域的灰度：
    mode='diff' 返回逐帧平均变化量（找切换、出现、点击），'bright' 返回逐帧平均亮度（找按下变暗、灭灯）。
    返回 (times, values)，times 为全片秒。"""
    vf = (f'crop={crop},' if crop else 'scale=192:108,') + 'format=gray'
    p = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', str(t0), '-i', film, '-t', str(dur), '-vf', vf, '-f', 'rawvideo', '-'], capture_output=True)
    w, h = (map(int, crop.split(':')[:2]) if crop else (192, 108))
    f = np.frombuffer(p.stdout, np.uint8).reshape(-1, h, w).astype(float)
    if mode == 'bright':
        return t0 + np.arange(len(f)) / 30, f.mean(axis=(1, 2))
    return t0 + np.arange(1, len(f)) / 30, np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))


def spikes(times, vals, k=2.0, gap=0.25):
    """变化量里超过 均值+k*标准差 的时刻（相邻 gap 秒内只留第一个）。"""
    th = vals.mean() + k * vals.std(); ev = []
    for t, v in zip(times, vals):
        if v > th and (not ev or t - ev[-1] > gap): ev.append(round(float(t), 2))
    return ev


def peaks_per_second(x):
    a = np.abs(x).max(axis=0)
    return [round(float(a[i * SR:(i + 1) * SR].max()), 2) for i in range(len(a) // SR)]
