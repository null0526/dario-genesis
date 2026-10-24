"""把第五章两段声音层（part_a 518.13–593.40、part_b 593.40–681.67，均 Sonnet 子代理）相加成整章，写 ch5-full-music.wav（全片时间线）。"""
import numpy as np
from scipy.io import wavfile

SR = 48000; DUR = 684.0
acc = np.zeros((int(DUR * SR), 2), np.float64)
for f in ['ch5-part-a-music.wav', 'ch5-part-b-music.wav']:
    sr, x = wavfile.read(f); assert sr == SR, f
    x = x.astype(np.float64)[:len(acc)]
    acc[:len(x)] += x
    print(f, round(len(x) / SR, 2), 's')
acc[:int(518.13 * SR)] = 0
t = int(681.67 * SR)
acc[t:] *= np.clip(1 - np.arange(len(acc) - t) / (0.5 * SR), 0, 1)[:, None]   # 跟章末淡黑
wavfile.write('ch5-full-music.wav', SR, acc.astype(np.float32))
print('ok peak', round(float(np.abs(acc).max()), 3))
