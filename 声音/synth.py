"""协调者（Claude）亲手写的配乐合成器：numpy/scipy 离线合成，48kHz 立体声。
乐器都是代码合成（拨弦、木槌、贝斯、垫音、玻璃钟、电钢琴、轻鼓），不用任何采样。
设计原则：音乐跟画面走——按旁白与画面事件的秒数落点，可在笑点前收住、在揭示处托和弦。"""
import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(20261022)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def m(name):
    """'D3' -> midi"""
    p, o = name[:-1], int(name[-1])
    return 12 * (o + 1) + NOTE[p]


class Bus:
    def __init__(self, dur):
        self.x = np.zeros((2, int(dur * SR) + SR * 8))

    def add(self, sig, t, gain=1.0, pan=0.0):
        i = int(round(t * SR))
        if i < 0:
            sig = sig[..., -i:]; i = 0
        if sig.ndim == 1:
            l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
            sig = np.vstack([sig * l * 1.414, sig * r * 1.414])
        n = min(sig.shape[1], self.x.shape[1] - i)
        if n > 0:
            self.x[:, i:i + n] += gain * sig[:, :n]


def env(n, a=0.005, d=0.0, s=1.0, r=0.05, hold=None):
    """线性 ADSR，n 为总样本；hold 为按住秒数（不含 release）。"""
    t = np.arange(n) / SR
    hold = (n / SR - r) if hold is None else hold
    e = np.where(t < a, t / max(a, 1e-6), 1.0)
    if d > 0:
        e = np.where((t >= a) & (t < a + d), 1 - (1 - s) * (t - a) / d, e)
        e = np.where(t >= a + d, s, e)
    rel = np.clip(1 - (t - hold) / max(r, 1e-6), 0, 1)
    return e * np.where(t > hold, rel, 1.0)


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc, SR * 0.45) / (SR / 2), 'low')
    return signal.lfilter(b, a, x, axis=-1)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'high')
    return signal.lfilter(b, a, x, axis=-1)


def bp(x, f1, f2, order=2):
    b, a = signal.butter(order, [f1 / (SR / 2), f2 / (SR / 2)], 'band')
    return signal.lfilter(b, a, x, axis=-1)


# ---------- 乐器 ----------
def pluck(note, dur=1.6, bright=0.5, decay=0.996):
    """Karplus-Strong 拨弦（用 lfilter 实现延迟线）。bright 控制激励的明亮度。"""
    f = hz(note); N = int(round(SR / f)); n = int(dur * SR)
    exc = rng.uniform(-1, 1, N)
    exc = lp(exc, 800 + 5000 * bright, 1)
    x = np.zeros(n); x[:N] = exc
    a = np.zeros(N + 2); a[0] = 1; a[N] = -decay / 2; a[N + 1] = -decay / 2
    y = signal.lfilter([1.0], a, x)
    y = lp(y, 2500 + 3000 * bright)
    y = hp(y, f * 0.7)   # 去掉 KS 梳状滤波在 0Hz 的共振（低频轰鸣）
    return y * env(n, 0.002, r=0.08) / (np.abs(y).max() + 1e-9)


def mallet(note, dur=1.2):
    """木槌（马林巴式）：三个分音各自衰减。"""
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(note)
    y = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.55)
         + 0.32 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t / 0.12)
         + 0.08 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t / 0.04))
    return y * env(n, 0.003, r=0.05)


def bass(note, dur, a=0.01, r=0.15):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(note)
    y = np.sin(2 * np.pi * f * t) + 0.18 * np.sin(4 * np.pi * f * t) + 0.06 * np.sin(6 * np.pi * f * t)
    return np.tanh(1.3 * y) * env(n, a, r=r)


def saw(f, t, phase=0.0):
    return 2 * ((f * t + phase) % 1.0) - 1


def pad(notes, dur, a=2.0, r=2.0, cutoff=1800, cutoff_end=None, detune=7):
    """去谐锯齿垫音：每个音 3 支、左右不同去谐，低通扫频可从 cutoff 开到 cutoff_end。"""
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros((2, n))
    for k, note in enumerate(notes):
        f = hz(note)
        for ch in (0, 1):
            for d in (-detune, 0, detune):
                dd = d * (1.0 if ch == 0 else -0.83)
                out[ch] += saw(f * 2 ** (dd / 1200), t, rng.random())
    out /= 3 * len(notes)
    if cutoff_end is None:
        out = lp(out, cutoff)
    else:  # 分段扫频
        seg = SR // 10; y = np.zeros_like(out); zi = None
        for s in range(0, n, seg):
            fc = cutoff * (cutoff_end / cutoff) ** (s / n)
            b, aa = signal.butter(2, fc / (SR / 2), 'low')
            if zi is None:
                zi = np.zeros((2, 2))
            y[:, s:s + seg], zi = signal.lfilter(b, aa, out[:, s:s + seg], axis=-1, zi=zi)
        out = y
    return out * env(n, a, r=r)


def glass(note, dur=3.0, ratio=3.5, index=2.2):
    """玻璃钟：FM，调制指数快速衰减。"""
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(note)
    I = index * np.exp(-t / 0.25)
    y = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * ratio * t))
    return y * np.exp(-t / (dur / 3.5)) * env(n, 0.002, r=0.2)


def ep(note, dur=2.0):
    """电钢琴（Rhodes 式）：1:1 FM ＋ 一点高频音叉声。"""
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(note)
    I = 1.4 * np.exp(-t / 0.35) + 0.25
    y = np.sin(2 * np.pi * f * t + I * np.sin(2 * np.pi * f * t))
    y += 0.12 * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t / 0.02)
    return y * np.exp(-t / 1.6) * env(n, 0.003, r=0.25)


def kick(dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 45 + 75 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.16) * env(n, 0.001, r=0.05)


def snare(dur=0.25):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = bp(rng.uniform(-1, 1, n), 900, 4500) * np.exp(-t / 0.07)
    tone = 0.4 * np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.04)
    return (nz * 1.6 + tone) * env(n, 0.001, r=0.03)


def hat(dur=0.06):
    n = int(dur * SR); t = np.arange(n) / SR
    return hp(rng.uniform(-1, 1, n), 7000) * np.exp(-t / 0.018)


def reverb(x, rt60=2.4, wet=0.3, predelay=0.018, damp=5500):
    """合成脉冲响应的卷积混响（左右去相关），不含任何噪声床——尾巴之外是数字静音。"""
    n = int(rt60 * 1.3 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal((2, n)) * np.exp(-6.91 * t / rt60)
    ir = lp(ir, damp, 1)
    ir[:, :int(predelay * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    w = np.vstack([signal.fftconvolve(x[0], ir[0])[:x.shape[1]], signal.fftconvolve(x[1], ir[1])[:x.shape[1]]])
    return x * (1 - wet) + w * wet * 2.2


def lufs_short(x):
    """粗略响度（K 加权近似：高通 60Hz + 高架省略），只用于相对电平。"""
    y = hp(x.mean(axis=0) if x.ndim == 2 else x, 60)
    return 10 * np.log10(np.mean(y ** 2) + 1e-12) - 0.691


# ---------- 点缀用的“半音效半音乐”声音（r2，10/22 用户：不要整段 BGM，要音效与一点音乐性混合的点缀） ----------
def thud(dur=0.6, f0=62, tone=None):
    """盖章/落定：低频闷击＋木头敲击，tone 给一组音高让它带一点和声色彩。"""
    n = int(dur * SR); t = np.arange(n) / SR
    f = f0 + 40 * np.exp(-t / 0.02)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)
    knock = bp(rng.uniform(-1, 1, n), 500, 1800) * np.exp(-t / 0.012) * 0.5
    y = y + knock
    if tone:
        for k, nt in enumerate(tone):
            y += 0.22 * mallet(nt, dur)[:n] * (0.8 ** k)
    return y * env(n, 0.001, r=0.05)


def paper(dur=0.3, f1=1500, f2=6000, peak=0.35):
    """纸张滑入/落下：一次性带通噪声，起落都快，不留尾巴（不是底噪）。"""
    n = int(dur * SR); t = np.arange(n) / SR
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2 * np.exp(-t / (dur * 0.6))
    e = np.where(t < dur * peak, e * (t / (dur * peak)), e)
    return bp(rng.uniform(-1, 1, n), f1, f2) * e


def tick(dur=0.05, f=3200):
    """机械键/打字的一下。"""
    n = int(dur * SR); t = np.arange(n) / SR
    return (bp(rng.uniform(-1, 1, n), f * 0.6, f * 1.6) * np.exp(-t / 0.006)
            + 0.3 * np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-t / 0.01))


def drone(notes, dur, a=3.0, r=2.5, cutoff=700):
    """低处的长音：正弦＋少量锯齿，几乎不动，用来托住一段悬而未决。"""
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for nt in notes:
        f = hz(nt)
        out += np.sin(2 * np.pi * f * t) + 0.25 * lp(saw(f * 1.002, t), cutoff)
    out /= len(notes)
    return out * env(n, a, r=r)


# ---------- r3 补充：界面与叙事点缀 ----------
def click(dur=0.05):
    """鼠标点击：两段极短的中高频敲击（按下/松开）。"""
    n = int(dur * SR); t = np.arange(n) / SR
    y = bp(rng.uniform(-1, 1, n), 1800, 6000) * np.exp(-t / 0.003)
    k = int(0.028 * SR)
    y[k:] += 0.6 * bp(rng.uniform(-1, 1, n - k), 2500, 7000) * np.exp(-(t[k:] - t[k]) / 0.002)
    return y


def toggle(dur=0.09):
    """开关拨动：带一点“咔嗒”体积的点击。"""
    n = int(dur * SR); t = np.arange(n) / SR
    return (bp(rng.uniform(-1, 1, n), 900, 4500) * np.exp(-t / 0.008)
            + 0.5 * np.sin(2 * np.pi * 420 * t) * np.exp(-t / 0.015))


def beep(note, dur=0.12, bright=0.35):
    """系统提示音：柔和方波（低通过），短促干净。"""
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(note)
    sq = np.sign(np.sin(2 * np.pi * f * t))
    y = (1 - bright) * np.sin(2 * np.pi * f * t) + bright * lp(sq, 3000)
    return y * env(n, 0.004, r=0.03)


def gliss(n0, n1, dur=1.5, kind='glass'):
    """音高滑动（藤蔓攀升、额度恢复）：FM 玻璃音沿对数音高滑。"""
    n = int(dur * SR); t = np.arange(n) / SR
    f = hz(n0) * (hz(n1) / hz(n0)) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph + 0.8 * np.sin(3.5 * ph))
    return y * env(n, 0.05, r=0.3)


def crunch(dur=0.22):
    """咬一口苹果：几段很短的碎裂噪声。"""
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k, t0 in enumerate([0.0, 0.025, 0.05, 0.08]):
        i = int(t0 * SR); m_ = n - i
        y[i:] += (0.9 ** k) * bp(rng.uniform(-1, 1, m_), 1500 + 600 * k, 7000) * np.exp(-np.arange(m_) / SR / 0.012)
    return y


def church_bell(note, dur=6.0):
    """低沉的教堂钟：几个不和谐分音（hum、prime、tierce、quint、nominal）各自衰减。"""
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(note)
    parts = [(0.5, 0.5, 4.0), (1.0, 1.0, 2.8), (1.19, 0.6, 2.0), (1.5, 0.35, 1.6), (2.0, 0.5, 1.4), (2.74, 0.2, 0.8), (3.0, 0.15, 0.6)]
    y = sum(a * np.sin(2 * np.pi * f * r * t + rng.random()) * np.exp(-t / d) for r, a, d in parts)
    return y * env(n, 0.002, r=0.5)


def tapestop(x, t0, dur, SRr=SR):
    """磁带停转：t0 起 dur 秒内播放速度从 1 降到 0，之后静音（作用于立体声 bus 数组，原地返回新数组）。"""
    i0 = int(t0 * SRr); n = int(dur * SRr)
    rate = np.linspace(1, 0, n) ** 1.5
    pos = i0 + np.cumsum(rate)
    seg = np.vstack([np.interp(pos, np.arange(x.shape[1]), x[c]) for c in range(x.shape[0])])
    seg *= np.linspace(1, 0, n) ** 0.5
    y = x.copy(); y[:, i0:i0 + n] = seg; y[:, i0 + n:] = 0
    return y
