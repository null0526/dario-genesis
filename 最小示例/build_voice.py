"""拼旁白：解码各段 mp3 -> 修首尾静音 -> 按停顿表拼连续 voice.wav -> timeline.json（含字幕分块时码）"""
import json, os, subprocess, re
import numpy as np
from scipy.io import wavfile
from script import SEGS, LEAD, TAIL

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000


def decode(path):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype="<f4").copy()


def trim(x, thr=0.004, pad=0.04):
    idx = np.where(np.abs(x) > thr)[0]
    a = max(0, idx[0] - int(pad * SR))
    b = min(len(x), idx[-1] + int(pad * SR))
    return x[a:b]


def gaps(x, min_len=0.10):
    """返回段内的静音区间（秒），10ms 帧 RMS 低于峰值的 -38 dB。"""
    hop = int(0.01 * SR)
    n = len(x) // hop
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    thr = np.percentile(rms, 90) * 10 ** (-38 / 20)
    low = rms < thr
    out, i = [], 0
    while i < n:
        if low[i]:
            j = i
            while j < n and low[j]:
                j += 1
            if (j - i) * 0.01 >= min_len and i > 5 and j < n - 5:
                out.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return out


def chunk_times(seg_dur, chunks, gp):
    """按分块字数比例 + 实测静音吸附，返回每块 (start,end)，相对段起点。"""
    n = len(chunks)
    if n == 1:
        return [(0.0, seg_dur)]
    w = [len(re.findall(r"[一-鿿]", c)) for c in chunks]
    cum = np.cumsum(w)[:-1] / sum(w) * seg_dur  # 比例预测的分界
    bounds = []
    used = set()
    for c in cum:
        best, bi = None, None
        for k, (a, b) in enumerate(gp):
            if k in used:
                continue
            mid = (a + b) / 2
            d = abs(mid - c)
            if d < 0.9 and (best is None or d < best):  # 只吸附 0.9 秒以内的静音
                best, bi = d, k
        if bi is None:
            bounds.append(float(c))
        else:
            used.add(bi)
            bounds.append((gp[bi][0] + gp[bi][1]) / 2)
    bounds = sorted(bounds)
    starts = [0.0] + bounds
    ends = bounds + [seg_dur]
    return list(zip(starts, ends))


def main():
    parts = [np.zeros(int(LEAD * SR), dtype=np.float32)]
    t = LEAD
    tl = {"sr": SR, "segments": []}
    for sid, text, chunks, pause in SEGS:
        x = trim(decode(os.path.join(HERE, "tts", f"{sid}.mp3")))
        dur = len(x) / SR
        gp = gaps(x)
        ct = chunk_times(dur, chunks, gp)
        tl["segments"].append({
            "id": sid, "start": t, "end": t + dur, "text": text,
            "gaps": [(t + a, t + b) for a, b in gp],
            "chunks": [{"text": c, "start": t + a, "end": t + b} for c, (a, b) in zip(chunks, ct)],
        })
        parts.append(x.astype(np.float32))
        t += dur
        parts.append(np.zeros(int(pause * SR), dtype=np.float32))
        t += pause
    parts.append(np.zeros(int(TAIL * SR), dtype=np.float32))
    t += TAIL
    y = np.concatenate(parts)
    tl["duration"] = len(y) / SR
    peak = np.abs(y).max()
    print("peak", peak, "dur", tl["duration"])
    wavfile.write(os.path.join(HERE, "voice.wav"), SR, (y / max(peak, 1e-9) * 0.9 * 32767).astype(np.int16))
    with open(os.path.join(HERE, "timeline.json"), "w", encoding="utf-8", newline="") as f:
        json.dump(tl, f, ensure_ascii=False, indent=1)
    for s in tl["segments"]:
        print(s["id"], round(s["start"], 2), round(s["end"], 2), [round(g[0], 2) for g in s["gaps"]])


main()
