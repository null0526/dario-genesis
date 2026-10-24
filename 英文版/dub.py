"""英文配音：每条字幕一段 TTS，按中文字幕的起点摆放，再和配乐层、成片片尾原声混成母带。

用法：
    python dub.py lines            # 写 tts_lines.tsv（id、起点、可用秒数、要读的英文），按它逐条生成 tts/<id>.wav|mp3
    python dub.py voice            # tts/ -> voice_en.wav，打印放不下、被推迟的句子
    python dub.py mix 成片.mp4      # voice_en.wav + ../声音/full-music.wav + 成片片尾原声 -> mix_en.wav

摆放：每句放在对应中文字幕的起点；放不下（会压到下一句）时先最多提前 0.25 秒起读，再最多加速到 1.12 倍，
仍放不下就顺延下一句并报告——这种句子应该回 translation.json 改短。
电平照原片：旁白每章归一到 -22 LUFS，配乐层整体 -4.49 dB，片尾（677.188 秒起）直接用成片原声，
整片做到 -16 LUFS、真峰 -1.5 dBTP（4 倍过采样限幅）。"""
import glob, json, os, subprocess, sys
import numpy as np
import pyloudnorm
from scipy.io import wavfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from burn import cues, OFF   # noqa: E402  同一份字幕时间表

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
CREDITS = 677.188                 # 片尾起点（方法手册第三层）
MUSIC_DB = -4.49
VOICE_LUFS, MASTER_LUFS, TP_DB = -22.0, -16.0, -1.5
EARLY, MAX_TEMPO, GAP = 0.25, 1.12, 0.08


def decode(path, ch=1, ss=None):
    cmd = ['ffmpeg', '-v', 'error'] + (['-ss', str(ss)] if ss is not None else []) + ['-i', path, '-vn', '-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, '<f4').copy()
    return x.reshape(-1, ch) if ch > 1 else x


def trim(x, thr=0.004, pad=0.03):
    idx = np.where(np.abs(x) > thr)[0]
    return x[max(0, idx[0] - int(pad * SR)):idx[-1] + int(pad * SR)] if len(idx) else x[:0]


def tempo(x, r):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', f'atempo={r:.4f}', '-f', 'f32le', '-'],
                       input=x.astype('<f4').tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, '<f4').copy()


def chapter_of(t):
    return max(n for n, o in OFF.items() if t >= o - 1e-6)


def lines():
    with open(os.path.join(HERE, 'tts_lines.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('id\tstart\tseconds\ttext\n')
        qs = cues()
        for k, q in enumerate(qs):
            nxt = qs[k + 1]['start'] if k + 1 < len(qs) else q['end'] + 1
            f.write(f"{q['c']}\t{q['start']:.2f}\t{nxt - q['start']:.2f}\t{q['say']}\n")
    print('tts_lines.tsv', len(qs), '句')


def voice():
    qs = cues(); dur = CREDITS + 1
    out = np.zeros(int(dur * SR), np.float32); placed = []; prev_end = 0.0; late = []
    for k, q in enumerate(qs):
        f = (glob.glob(os.path.join(HERE, 'tts', q['c'] + '.*')) or [None])[0]
        assert f, f"缺 tts/{q['c']}.wav"
        x = trim(decode(f)); d = len(x) / SR
        win_end = (qs[k + 1]['start'] if k + 1 < len(qs) else q['end'] + 2) - GAP
        t0 = max(q['start'], prev_end + GAP)
        if t0 + d > win_end: t0 = max(min(t0, max(q['start'] - EARLY, prev_end + GAP)), win_end - d)
        if t0 + d > win_end:
            r = min(MAX_TEMPO, d / max(win_end - t0, 1e-3)); x = tempo(x, r); d = len(x) / SR
            if t0 + d > win_end + 0.02: late.append((q['c'], round(t0 + d - win_end, 2), q['say']))
        i = int(t0 * SR); out[i:i + len(x)] += x[:len(out) - i]
        placed.append({'c': q['c'], 'start': round(t0, 3), 'end': round(t0 + d, 3), 'target': round(q['start'], 3)})
        prev_end = t0 + d
    meter = pyloudnorm.Meter(SR)
    for n in OFF:         # 每章归一到 -22 LUFS
        a = int(OFF[n] * SR); b = int((OFF[n + 1] if n + 1 in OFF else CREDITS) * SR)
        seg = out[a:b]; g = VOICE_LUFS - meter.integrated_loudness(seg.astype(np.float64))
        out[a:b] = seg * 10 ** (g / 20); print(f'第{n}章旁白增益 {g:+.1f} dB')
    wavfile.write(os.path.join(HERE, 'voice_en.wav'), SR, out)
    json.dump(placed, open(os.path.join(HERE, 'voice_en.json'), 'w'), indent=0)
    drift = [(p['c'], round(p['start'] - p['target'], 2)) for p in placed if abs(p['start'] - p['target']) > 0.3]
    print('起点偏离中文超过 0.3 秒：', drift or '无')
    print('放不下、顺延了下一句（要改短）：', late or '无')


def mix(film):
    v = wavfile.read(os.path.join(HERE, 'voice_en.wav'))[1].astype(np.float64)
    m = wavfile.read(os.path.join(HERE, '..', '声音', 'full-music.wav'))[1].astype(np.float64) * 10 ** (MUSIC_DB / 20)
    orig = decode(film, 2).astype(np.float64); n = len(orig)
    y = np.zeros((n, 2)); c = int(CREDITS * SR)
    y[:min(c, len(m))] += m[:min(c, len(m))]; y[:min(c, len(v))] += v[:min(c, len(v)), None]
    fade = int(0.02 * SR); ramp = np.linspace(0, 1, fade)[:, None]
    y[c:c + fade] = y[c:c + fade] * (1 - ramp) + orig[c:c + fade] * ramp; y[c + fade:] = orig[c + fade:]
    g = MASTER_LUFS - pyloudnorm.Meter(SR).integrated_loudness(y); y *= 10 ** (g / 20)
    tmp = os.path.join(HERE, 'mix_pre.wav'); wavfile.write(tmp, SR, y.astype(np.float32))
    lim = 10 ** (TP_DB / 20)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af',
                    f'aresample=192000,alimiter=limit={lim:.4f}:attack=2:release=60:level=disabled,aresample=48000',
                    '-c:a', 'pcm_f32le', os.path.join(HERE, 'mix_en.wav')], check=True)
    os.remove(tmp)
    print(f'混音增益 {g:+.1f} dB -> mix_en.wav')
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', os.path.join(HERE, 'mix_en.wav'), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    print('\n'.join(l for l in r.splitlines()[-12:] if 'I:' in l or 'Peak:' in l))


if __name__ == '__main__':
    {'lines': lines, 'voice': voice, 'mix': lambda: mix(sys.argv[2])}[sys.argv[1]]()
