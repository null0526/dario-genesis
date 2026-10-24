"""成片 -> 英文版：中文字幕所在的带子在每条字幕显示期间用 delogo 抹掉，再烧上英文字幕；可选换成英文配音。

用法：
    python burn.py 成片.mp4 out.mp4                    # 保留原声，抹中文字幕、烧英文字幕
    python burn.py 成片.mp4 out.mp4 --audio mix_en.wav  # 同时换成英文配音混音
    python burn.py 成片.mp4 check --stills              # 不出片，只在每条字幕中点抽一帧，拼成 check/sheet-*.jpg 核对
    加 --start 秒 --dur 秒 只处理一段（试看）
    无字幕版：python burn.py nosub.mp4 out.mp4 --offset 3.0426 --no-mask   （片头多 3.0426 秒，不用抹字幕）

中文字幕的位置取自镜头源码：46px，水平居中，基线 y=998（1080-82），亮色带阴影或纸面墨色。
每条英文字幕抹掉的范围 = 它覆盖的那几条中文分块里最宽的一条 + 余量；时间 = 这些分块的起止（各放宽 0.06 秒）。
英文字幕颜色按这条字幕中点时字幕带的平均亮度自动选：暗背景用亮字，纸面用墨色字。
抹除都用 delogo（从框边插值，不会把框外的画面内容搬进来）。纸面上 delogo 会留一块带竖纹的光滑补丁，
所以纸面字幕再在同一位置叠一层：补丁轻微模糊后加回颗粒。框宽按 4 档分组，每档一条支路，开销小。"""
import argparse, json, os, re, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', '数据')
OFF = {1: 0.0, 2: 190.5333, 3: 353.1333, 4: 421.8667, 5: 518.1333}
W, H = 1920, 1080
BAND_Y, BAND_H = 928, 104          # 中文字幕带（含阴影）：y 928–1032
PAD = 0.06
BUCKET = 150                       # 纸面补丁宽度分档（像素）


def load_chapter(n):
    s = open(os.path.join(DATA, f'ch{n}.js'), encoding='utf-8').read()
    return json.loads(s[s.index('{'):].rstrip().rstrip(';'))


def zh_width(text):
    wide = len(re.findall(r'[　-〿一-鿿＀-￯“”‘’《》·—…]', text))
    return wide * 46 + (len(text) - wide) * 26


def cues(offset=0.0):
    caps = {n: load_chapter(n)['captions'] for n in OFF}
    out = []
    for item in json.load(open(os.path.join(HERE, 'translation.json'), encoding='utf-8')):
        first, _, last = item['c'].partition('-')
        ch, a = map(int, first.split('.')); b = int((last or first).split('.')[1])
        span = caps[ch][a:b + 1]; shown = [c for c in span if c.get('kind') != 'screen' and c['text'].strip('”“ ')]
        o = OFF[ch] + offset
        out.append({'c': item['c'], 'en': item['en'], 'say': item.get('say', item['en']), 'start': span[0]['start'] + o, 'end': span[-1]['end'] + o,
                    'mask': (shown[0]['start'] + o - PAD, shown[-1]['end'] + o + PAD) if shown else None,
                    'mw': max((zh_width(c['text']) for c in shown), default=0)})
    out.sort(key=lambda q: q['start'])
    return out


def band_luma(video, t):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1',
                        '-vf', f'crop={W - 400}:{BAND_H}:200:{BAND_Y},scale=152:10,format=gray', '-f', 'rawvideo', '-'],
                       capture_output=True, check=True)
    return float(np.frombuffer(p.stdout, np.uint8).mean()) if p.stdout else 0.0


def ts(t):
    t = max(t, 0); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f'{h}:{m:02d}:{s:05.2f}'


def wrap(text, n=46):
    if len(text) <= n: return text
    w = text.split()
    k = min(range(1, len(w)), key=lambda k: max(len(' '.join(w[:k])), len(' '.join(w[k:]))))
    return ' '.join(w[:k]) + r'\N' + ' '.join(w[k:])


def write_ass(qs, path, shift, signs=None, t_end=1e9):
    """旁白字幕；signs（signs.json）另加画面中文的顶部标注和片尾整页替换。signs 里是视频时间。"""
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Light,Inter,46,&H00ECF2F4,&H00ECF2F4,&H70000000,&H90000000,0,0,0,0,100,100,0,0,1,2.2,1.2,2,120,120,72,1
Style: Ink,Inter,46,&H001C2226,&H001C2226,&H00D9E1E4,&H00000000,0,0,0,0,100,100,0,0,1,1.6,0,2,120,120,72,1
Style: Sign,Inter,28,&H00F2F2F2,&H00F2F2F2,&H60000000,&H00000000,0,0,0,0,100,100,0,0,3,8,0,8,90,90,16,1
Style: Box,Inter,20,&H00000000,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: CredLabel,Source Serif 4 Light,34,&H00858886,&H00858886,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,0,5,0,0,0,1
Style: CredName,Source Serif 4,73,&H00E0E7E4,&H00E0E7E4,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: CredName2,Source Serif 4,62,&H00E6E8E1,&H00E6E8E1,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: CredTruth,Source Serif 4,42,&H00B2B4AE,&H00B2B4AE,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,5,0,0,0,1
Style: CredNote,Source Serif 4,52,&H00E6E7E0,&H00E6E7E0,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,5,0,0,0,1
Style: CredNoteDim,Source Serif 4,52,&H00848988,&H00848988,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [head]
    for k, q in enumerate(qs):
        nxt = qs[k + 1]['start'] if k + 1 < len(qs) else q['end'] + 0.8
        end = max(q['end'], min(nxt - 0.04, q['end'] + 0.3))
        halo = ''
        lines.append(f"Dialogue: 0,{ts(q['start'] - shift)},{ts(end - shift)},{q['style']},,0,0,0,,{{\\fad(80,80){halo}}}{wrap(q['en'])}\n")
    if signs:
        for t0, t1, text in signs['notes']:
            if t1 > shift and t0 < t_end:
                lines.append(f"Dialogue: 2,{ts(t0 - shift)},{ts(t1 - shift)},Sign,,0,0,0,,{{\\fad(150,150)}}{text}\n")
        for c in signs['credits']:      # 片尾：不透明黑框盖住中文（黑底上看不出），英文跟原片同帧淡入淡出
            if not (c['t1'] > shift and c['t0'] < t_end): continue
            x0, y0, x1, y1 = c['box']; s, e = ts(c['t0'] - shift), ts(c['t1'] - shift)
            lines.append(f"Dialogue: 3,{s},{e},Box,,0,0,0,,{{\\an7\\pos(0,0)\\p1}}m {x0} {y0} l {x1} {y0} l {x1} {y1} l {x0} {y1}{{\\p0}}\n")
            for style, an, x, y, text in c['lines']:
                lines.append(f"Dialogue: 4,{s},{e},{style},,0,0,0,,{{\\an{an}\\pos({x},{y})\\fad({c['fin']},{c['fout']})}}{text}\n")
    open(path, 'w', encoding='utf-8', newline='\n').write(''.join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video'); ap.add_argument('out')
    ap.add_argument('--audio'); ap.add_argument('--stills', action='store_true')
    ap.add_argument('--start', type=float, default=0.0); ap.add_argument('--dur', type=float)
    ap.add_argument('--offset', type=float, default=0.0, help='视频比原成片时间轴晚多少秒')
    ap.add_argument('--no-mask', action='store_true', help='视频本来没有中文字幕，不抹')
    ap.add_argument('--signs', help='画面中文的标注和片尾替换（signs.json，视频时间）')
    a = ap.parse_args()
    qs = cues(a.offset)
    end_t = a.start + a.dur if a.dur else 1e9
    qs_win = [q for q in qs if q['end'] > a.start and q['start'] < end_t]
    for q in qs_win:
        q['luma'] = band_luma(a.video, (q['start'] + q['end']) / 2)
        q['style'] = 'Ink' if q['luma'] > 150 else 'Light'
    print('Ink 样式:', [q['c'] for q in qs_win if q['style'] == 'Ink'])

    if a.stills:      # 每条字幕中点一帧，标出抹除框，拼图核对位置
        os.makedirs(a.out, exist_ok=True)
        for k in range(0, len(qs_win), 24):
            tiles = []
            for q in qs_win[k:k + 24]:
                t = (q['start'] + q['end']) / 2
                p = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', a.video, '-frames:v', '1', '-vf',
                                    f"crop=1920:300:0:780,drawbox=x={960 - q['mw'] // 2 - 40}:y={BAND_Y - 780}:w={q['mw'] + 80}:h={BAND_H}:color=red@0.9:t=3,"
                                    f"drawtext=text='{q['c']} L{q['luma']:.0f}':x=10:y=10:fontsize=40:fontcolor=yellow,scale=640:100", '-f', 'image2', '-c:v', 'png', '-'],
                                   capture_output=True, check=True)
                tiles.append(p.stdout)
            listing = os.path.join(a.out, f'tiles-{k:03d}'); os.makedirs(listing, exist_ok=True)
            for i, b in enumerate(tiles): open(os.path.join(listing, f'{i:02d}.png'), 'wb').write(b)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-pattern_type', 'glob', '-i', os.path.join(listing, '*.png'),
                            '-vf', 'tile=3x8', '-frames:v', '1', os.path.join(a.out, f'sheet-{k:03d}.jpg')], check=True)
        print('stills ->', a.out); return

    signs = json.load(open(a.signs, encoding='utf-8')) if a.signs else None
    ass = os.path.join(HERE, 'en.ass'); write_ass(qs_win, ass, a.start, signs, end_t)
    delogo, ink = [], {}
    for q in qs_win:
        if not q['mask'] or a.no_mask: continue
        s0, s1 = q['mask'][0] - a.start, q['mask'][1] - a.start
        w = q['mw'] + 80; x = max(1, 960 - w // 2)
        delogo.append(f"delogo=x={x}:y={BAND_Y}:w={min(w, W - 2 - x)}:h={BAND_H}:enable='between(t,{s0:.3f},{s1:.3f})'")
        if q['style'] == 'Ink':
            bw = min(W - 40, -(-w // BUCKET) * BUCKET)
            ink.setdefault(bw, []).append(f'between(t,{s0:.3f},{s1:.3f})')
    graph = f"[0:v]{','.join(delogo) or 'null'}"
    if ink:
        graph += f",split={len(ink) + 1}[d0]" + ''.join(f'[p{i}]' for i in range(len(ink))) + ';'
        for i, (bw, wins) in enumerate(sorted(ink.items())):
            graph += (f"[p{i}]crop={bw}:{BAND_H}:{960 - bw // 2}:{BAND_Y},boxblur=8:2,noise=alls=7:allf=t[g{i}];"
                      f"[d{i}][g{i}]overlay={960 - bw // 2}:{BAND_Y}:enable='{'+'.join(wins)}'[d{i + 1}];")
        graph += f"[d{len(ink)}]"
    else:
        graph += ','
    graph += f"ass={ass}[v]"
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', str(a.start), '-i', a.video]
    if a.audio: cmd += ['-ss', str(a.start), '-i', a.audio]
    if a.dur: cmd += ['-t', str(a.dur)]
    cmd += ['-filter_complex', graph, '-map', '[v]', '-map', '1:a' if a.audio else '0:a?',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
            '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
            '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-movflags', '+faststart', a.out]
    subprocess.run(cmd, check=True)
    print('ok', a.out)


if __name__ == '__main__':
    main()
