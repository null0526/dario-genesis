"""把五章声音层拼成全片时间线 full-music.wav（各章 wav 已是全片时间、章外为 0，直接相加）。"""
import numpy as np
from scipy.io import wavfile

SR = 48000; DUR = 681.6666
acc = np.zeros((int(DUR * SR), 2), np.float64)
for f in ['ch1-full-music.wav', 'ch2-full-music.wav', 'ch3-music.wav', 'ch4-music.wav', 'ch5-full-music.wav']:
    sr, x = wavfile.read(f); assert sr == SR, f
    x = x.astype(np.float64)[:len(acc)]
    acc[:len(x)] += x
    print(f, round(len(x) / SR, 2), 's')
wavfile.write('full-music.wav', SR, acc.astype(np.float32))
print('ok peak', round(float(np.abs(acc).max()), 3))
