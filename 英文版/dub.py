"""英文配音：每条字幕一段 TTS，按中文字幕的起点摆放，再和配乐层、成片片尾原声混成母带。

用法：
    python dub.py lines            # 写 tts_lines.tsv（id、起点、可用秒数、要读的英文），按它逐条生成 tts/<id>.wav|mp3
    python dub.py voice --tts tts/polly-Matthew        # 某个音色的逐句音频 -> voice_en.wav，打印放不下、被推迟的句子
    python dub.py mix nosub.mp4 --offset 3.0426        # voice_en.wav + ../声音/full-music.wav + 成片片尾原声 -> mix_en.wav
    python dub.py sample nosub.mp4 tts/polly-Matthew --offset 3.0426 --until 33
                                                       # 试听样片：前 33 秒（原成片时间）的配音 + 配乐 + 英文字幕 -> samples/<音色>.mp4
    python dub.py record voice_en.json alignment.tsv   # 对齐记录：每句目标起点、实际起止、偏差、超窗，末尾附汇总

摆放：每句放在对应中文字幕的起点；放不下（会压到下一句）时先最多提前 0.25 秒起读，再最多加速到 1.12 倍，
仍放不下就顺延下一句并报告——这种句子应该回 translation.json 改短。
电平照原片：旁白每章归一到 -22 LUFS，配乐层整体 -4.49 dB，片尾（677.188 秒起）直接用成片原声，
整片做到 -16 LUFS、真峰 -1.5 dBTP（4 倍过采样限幅）。"""
import argparse, glob, json, os, subprocess, sys
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


def voice(tts='tts', out_name='voice_en', until=None):
    qs = [q for q in cues() if until is None or q['start'] < until]; dur = (until + 2) if until else CREDITS + 1
    out = np.zeros(int(dur * SR), np.float32); placed = []; prev_end = 0.0; late = []
    for k, q in enumerate(qs):
        f = next((x for e in ('wav', 'mp3') for x in glob.glob(os.path.join(HERE, tts, f"{q['c']}.{e}"))), None)
        assert f, f"缺 {tts}/{q['c']}.wav"
        x = trim(decode(f)); d = len(x) / SR
        win_end = (qs[k + 1]['start'] if k + 1 < len(qs) else min(q['end'] + 2, dur - 0.1)) - GAP
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
        a = int(OFF[n] * SR); b = min(int((OFF[n + 1] if n + 1 in OFF else CREDITS) * SR), len(out))
        if b - a < SR * 3: continue
        seg = out[a:b]; g = VOICE_LUFS - meter.integrated_loudness(seg.astype(np.float64))
        out[a:b] = seg * 10 ** (g / 20); print(f'第{n}章旁白增益 {g:+.1f} dB')
    wavfile.write(os.path.join(HERE, out_name + '.wav'), SR, out)
    json.dump(placed, open(os.path.join(HERE, out_name + '.json'), 'w'), indent=0)
    drift = [(p['c'], round(p['start'] - p['target'], 2)) for p in placed if abs(p['start'] - p['target']) > 0.3]
    print('起点偏离中文超过 0.3 秒：', drift or '无')
    print('放不下、顺延了下一句（要改短）：', late or '无')


def mix(film, offset=0.0, voice_name='voice_en', out_name='mix_en', until=None):
    v = wavfile.read(os.path.join(HERE, voice_name + '.wav'))[1].astype(np.float64)
    m = wavfile.read(os.path.join(HERE, '..', '声音', 'full-music.wav'))[1].astype(np.float64) * 10 ** (MUSIC_DB / 20)
    orig = decode(film, 2).astype(np.float64); n = len(orig)
    y = np.zeros((n, 2)); i0 = int(round(offset * SR)); c = int((CREDITS + offset) * SR); k = c - i0   # 配乐、旁白整体后移 offset
    y[i0:i0 + min(k, len(m))] += m[:min(k, len(m))]; y[i0:i0 + min(k, len(v))] += v[:min(k, len(v)), None]
    fade = int(0.02 * SR); ramp = np.linspace(0, 1, fade)[:, None]
    y[c:c + fade] = y[c:c + fade] * (1 - ramp) + orig[c:c + fade] * ramp; y[c + fade:] = orig[c + fade:]
    if until: y = y[:int((until + offset) * SR)]       # 试听样片只取前一段
    g = MASTER_LUFS - pyloudnorm.Meter(SR).integrated_loudness(y); y *= 10 ** (g / 20)
    tmp = os.path.join(HERE, 'mix_pre.wav'); wavfile.write(tmp, SR, y.astype(np.float32))
    lim = 10 ** (TP_DB / 20)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af',
                    f'aresample=192000,alimiter=limit={lim:.4f}:attack=2:release=60:level=disabled,aresample=48000',
                    '-c:a', 'pcm_f32le', os.path.join(HERE, out_name + '.wav')], check=True)
    os.remove(tmp)
    print(f'混音增益 {g:+.1f} dB -> {out_name}.wav')
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', os.path.join(HERE, out_name + '.wav'), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    print('\n'.join(l for l in r.splitlines()[-12:] if 'I:' in l or 'Peak:' in l))


def record(placed_json, out_tsv):
    """对齐记录（原成片时间，秒；无字幕版要加 3.0426）。偏差 = 实际起点 - 中文起点；
    超窗 = 句末超过"下一句中文起点 - GAP"的秒数（摆放器会顺延下一句）。"""
    placed = json.load(open(os.path.join(HERE, placed_json)))
    text = {r.split('\t')[0]: r.rstrip('\n').split('\t')[3] for r in open(os.path.join(HERE, 'tts_lines.tsv'), encoding='utf-8').readlines()[1:]}
    rows, over = [], []
    for k, p in enumerate(placed):
        nxt = placed[k + 1]['target'] if k + 1 < len(placed) else None
        ov = max(0.0, p['end'] - (nxt - GAP)) if nxt is not None else 0.0
        rows.append((p['c'], p['target'], p['start'], p['end'], p['start'] - p['target'], ov, text.get(p['c'], '')))
        if ov > 0.02: over.append(ov)
    d = [r[4] for r in rows]
    summary = (f"# {len(rows)} 句；起点偏差在 ±0.3 秒内 {sum(abs(x) <= 0.3 for x in d)} 句，最早 {min(d):+.3f}，最晚 {max(d):+.3f}；"
               f"超窗 {len(over)} 句" + (f"（{min(over):.2f}–{max(over):.2f} 秒）" if over else ''))
    with open(os.path.join(HERE, out_tsv), 'w', encoding='utf-8', newline='\n') as f:
        f.write('id\ttarget\tstart\tend\tdelay\toverflow\ttext\n')
        for r in rows: f.write(f"{r[0]}\t{r[1]:.3f}\t{r[2]:.3f}\t{r[3]:.3f}\t{r[4]:+.3f}\t{r[5]:.3f}\t{r[6]}\n")
        f.write(summary + '\n')
    print(summary)


def sample(film, tts, offset, until):
    name = os.path.basename(tts.rstrip('/')); os.makedirs(os.path.join(HERE, 'samples'), exist_ok=True)
    voice(tts, f'samples/{name}-voice', until)
    mix(film, offset, f'samples/{name}-voice', f'samples/{name}-mix', until)
    full = os.path.join(HERE, 'samples', f'{name}-full.mp4'); small = os.path.join(HERE, 'samples', f'{name}.mp4')
    subprocess.run([sys.executable, os.path.join(HERE, 'burn.py'), film, full, '--offset', str(offset), '--no-mask',
                    '--audio', os.path.join(HERE, 'samples', f'{name}-mix.wav'), '--dur', str(until + offset + 0.5)], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', full, '-vf', 'scale=1280:-2', '-c:v', 'libx264', '-preset', 'fast', '-crf', '24',
                    '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', small], check=True)
    os.remove(full); print('样片 ->', small)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['lines', 'voice', 'mix', 'sample', 'record']); ap.add_argument('args', nargs='*')
    ap.add_argument('--tts', default='tts'); ap.add_argument('--offset', type=float, default=0.0); ap.add_argument('--until', type=float)
    a = ap.parse_args()
    if a.cmd == 'lines': lines()
    elif a.cmd == 'voice': voice(a.tts, until=a.until)
    elif a.cmd == 'mix': mix(a.args[0], a.offset, until=a.until)
    elif a.cmd == 'record': record(a.args[0], a.args[1])
    else: sample(a.args[0], a.args[1], a.offset, a.until or 33.0)
