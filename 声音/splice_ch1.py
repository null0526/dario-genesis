"""把第一章三段声音层（ch1_seq 0–123、part_a 122.85–155.17 协调者、part_b 155.17–191 Sonnet 子代理）相加成整章，写 ch1-full-music.wav。"""
import numpy as np
from scipy.io import wavfile

SR = 48000; DUR = 191.3
acc = np.zeros((int(DUR * SR), 2), np.float64)
for f in ['ch1-seq-music.wav', 'ch1-part-a-music.wav', 'ch1-part-b-music.wav']:
    sr, x = wavfile.read(f); assert sr == SR, f
    x = x.astype(np.float64)[:len(acc)]
    acc[:len(x)] += x
    print(f, round(len(x) / SR, 2), 's')
acc[int(190.33 * SR):] *= np.clip(1 - np.arange(len(acc) - int(190.33 * SR)) / (0.5 * SR), 0, 1)[:, None]   # 跟章末淡黑
wavfile.write('ch1-full-music.wav', SR, acc.astype(np.float32))
print('ok peak', round(float(np.abs(acc).max()), 3))
