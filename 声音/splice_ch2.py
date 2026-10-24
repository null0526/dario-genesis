"""把第二章两段声音层（part_a 190.53–278.15、part_b 278.15–352.93，均 Sonnet 子代理）相加成整章，写 ch2-full-music.wav（全片时间线）。"""
import numpy as np
from scipy.io import wavfile

SR = 48000; DUR = 356.0
acc = np.zeros((int(DUR * SR), 2), np.float64)
for f in ['ch2-part-a-music.wav', 'ch2-part-b-music.wav']:
    sr, x = wavfile.read(f); assert sr == SR, f
    x = x.astype(np.float64)[:len(acc)]
    acc[:len(x)] += x
    print(f, round(len(x) / SR, 2), 's')
acc[:int(190.53 * SR)] = 0
t = int(352.43 * SR)
acc[t:] *= np.clip(1 - np.arange(len(acc) - t) / (0.5 * SR), 0, 1)[:, None]   # 跟章末淡黑
wavfile.write('ch2-full-music.wav', SR, acc.astype(np.float32))
print('ok peak', round(float(np.abs(acc).max()), 3))
