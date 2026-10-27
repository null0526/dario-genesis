"""英文字幕：translation.json + ../数据/chN.js -> en.srt、zh.srt（全片时间），并检查覆盖和语速。

translation.json 每条 {"c": "章.起-章.止", "en": 字幕, "say": 可选的 TTS 读法}，c 指 数据/chN.js 里 captions 的下标范围，
时间取范围内第一条的 start 到最后一条的 end，再加该章在全片里的起点（方法手册第三层）。
语速按"这条字幕时长 + 到下一条的空隙（最多 0.8 秒）"算每秒词数，超过 3.0 的列出来，配音时要优先改短。
用法：python make_subs.py                                  # 原成片时间（r7，700.907 秒）
      python make_subs.py --offset 3.0426 --suffix nosub     # 无字幕版（片头多 3.0426 秒静音）-> en-nosub.srt"""
import argparse, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', '数据')
OFF = {1: 0.0, 2: 190.5333, 3: 353.1333, 4: 421.8667, 5: 518.1333}   # 各章零点在全片里的秒数
MAX_LINE = 46
FAST = 3.0


def load_chapter(n):
    s = open(os.path.join(DATA, f'ch{n}.js'), encoding='utf-8').read()
    return json.loads(s[s.index('{'):].rstrip().rstrip(';'))


def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def wrap(text):
    """一行放得下就一行；否则拆成尽量等长的两行。"""
    if len(text) <= MAX_LINE:
        return [text]
    words = text.split(); best = None
    for k in range(1, len(words)):
        a, b = ' '.join(words[:k]), ' '.join(words[k:])
        score = max(len(a), len(b))
        if best is None or score < best[0]: best = (score, [a, b])
    return best[1]


def words(text):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.-]*", text))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--offset', type=float, default=0.0); ap.add_argument('--suffix', default='')
    args = ap.parse_args(); sfx = f'-{args.suffix}' if args.suffix else ''
    caps = {n: load_chapter(n)['captions'] for n in OFF}
    cues, seen = [], set()
    for item in json.load(open(os.path.join(HERE, 'translation.json'), encoding='utf-8')):
        first, _, last = item['c'].partition('-')          # "1.00-1.02" 或 "1.03"
        ch, a = map(int, first.split('.')); b = int((last or first).split('.')[1])
        for i in range(a, b + 1):
            assert (ch, i) not in seen, f'重复 {ch}.{i}'; seen.add((ch, i))
        c = caps[ch]
        cues.append({'c': item['c'], 'start': c[a]['start'] + OFF[ch] + args.offset, 'end': c[b]['end'] + OFF[ch] + args.offset, 'en': item['en'],
                     'say': item.get('say', item['en']), 'zh': ''.join(x['text'] for x in c[a:b + 1] if x.get('kind') != 'screen')})
    missing = [f'{n}.{i:02d}' for n in caps for i in range(len(caps[n])) if (n, i) not in seen]
    assert not missing, f'没覆盖到的字幕 {missing}'
    cues.sort(key=lambda q: q['start'])

    srt_en, srt_zh, slow = [], [], []
    for k, q in enumerate(cues):
        nxt = cues[k + 1]['start'] if k + 1 < len(cues) else q['end'] + 0.8
        assert q['end'] <= nxt + 1e-6, f"字幕重叠 {q['c']}"
        avail = q['end'] - q['start'] + min(0.8, nxt - q['end'])
        q['wps'] = words(q['say']) / avail
        lines = wrap(q['en'])
        if len(lines) > 1 and max(map(len, lines)) > MAX_LINE: slow.append(f"  过长 {q['c']}: {q['en']}")
        end = max(q['end'], min(nxt - 0.04, q['end'] + 0.3))   # 显示时间往后多留最多 0.3 秒，不压下一条
        srt_en.append(f"{k + 1}\n{ts(q['start'])} --> {ts(end)}\n" + '\n'.join(lines) + '\n')
        srt_zh.append(f"{k + 1}\n{ts(q['start'])} --> {ts(end)}\n{q['zh'].rstrip('，。；：')}\n")
    open(os.path.join(HERE, f'en{sfx}.srt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(srt_en))
    open(os.path.join(HERE, f'zh{sfx}.srt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(srt_zh))

    tot = sum(words(q['say']) for q in cues)
    print(f'{len(cues)} 条字幕，覆盖 {len(seen)} 条中文分块；英文 {tot} 词（按读法计）')
    fast = [q for q in cues if q['wps'] > FAST]
    print(f'语速超过 {FAST} 词/秒的 {len(fast)} 条：')
    for q in fast: print(f"  {q['c']:10s} {q['wps']:.2f}  {q['say']}")
    for s in slow: print(s)


main()
