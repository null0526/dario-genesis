"""画面中文盘点：按 fps 抽帧做 OCR（RapidOCR），只留含汉字的框，按"位置相近 + 文字相同"并成条目。

用法：python ocr_inventory.py nosub.mp4 [--fps 1] -> ocr_raw.json（逐帧）、ocr_items.json / ocr_items.tsv（条目：首末时间、框、文字）
时间是视频时间（无字幕版含片头 3.0426 秒）。"""
import argparse, json, os, re, subprocess, tempfile
import numpy as np
from rapidocr_onnxruntime import RapidOCR

HERE = os.path.dirname(os.path.abspath(__file__))
HAN = re.compile(r'[一-鿿]')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('--fps', type=float, default=1.0)
    a = ap.parse_args()
    eng = RapidOCR(); raw = []
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['ffmpeg', '-v', 'error', '-i', a.video, '-vf', f'fps={a.fps}', '-q:v', '2', os.path.join(d, '%05d.jpg')], check=True)
        files = sorted(os.listdir(d))
        for k, f in enumerate(files):
            t = (k + 0.5) / a.fps         # fps 滤镜取的是每个区间中点附近的帧
            res, _ = eng(os.path.join(d, f))
            for box, text, score in res or []:
                score = float(score)
                if HAN.search(text) and score > 0.6:
                    xs = [p[0] for p in box]; ys = [p[1] for p in box]
                    raw.append({'t': round(t, 2), 'text': text, 'score': round(float(score), 3),
                                'box': [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]})
            if k % 60 == 0: print(f'{k}/{len(files)} frames, {len(raw)} hits', flush=True)
    json.dump(raw, open(os.path.join(HERE, 'ocr_raw.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

    # 并条目：同一文字、框中心相距 < 60px、时间相邻（间隔不超过 2/fps）
    items = []
    for r in sorted(raw, key=lambda r: r['t']):
        cx, cy = (r['box'][0] + r['box'][2]) / 2, (r['box'][1] + r['box'][3]) / 2
        for it in items:
            if it['text'] == r['text'] and abs(it['cx'] - cx) < 60 and abs(it['cy'] - cy) < 60 and r['t'] - it['t1'] <= 2.01 / a.fps:
                it['t1'] = r['t']; it['n'] += 1; break
        else:
            items.append({'t0': r['t'], 't1': r['t'], 'text': r['text'], 'cx': cx, 'cy': cy, 'box': r['box'], 'n': 1})
    json.dump(items, open(os.path.join(HERE, 'ocr_items.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    with open(os.path.join(HERE, 'ocr_items.tsv'), 'w', encoding='utf-8') as f:
        f.write('t0\tt1\tbox\ttext\n')
        for it in items: f.write(f"{it['t0']}\t{it['t1']}\t{it['box']}\t{it['text']}\n")
    print(len(raw), 'hits ->', len(items), 'items')


main()
