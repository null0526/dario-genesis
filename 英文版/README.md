# 英文版

把《达里奥创世录》做成英文版发布到 YouTube 用到的译稿、字幕轨和脚本。成片视频不在 git 里，见 Release 附件。

## 当前版本

- **画面**：用的是无字幕原片，不烧字幕。这个版本片头比原成片多 3.0426 秒静音。片尾四页原位替换成英文，字体是原片的西文衬线 Source Serif 4，淡入淡出与原片同帧。
- **音轨**：英文配音用本地 TTS Kokoro-82M（音色 `am_michael`），按中文旁白逐句对齐。配乐层用 `声音/` 的脚本重建。电平沿用原片的母带规格：旁白每章 −22 LUFS，配乐 −4.49 dB，整片 −16 LUFS、真峰 −1.5 dBTP。
- **字幕**：`en-nosub.srt`（英文）和 `zh-nosub.srt`（中文），作为字幕轨单独上传。
- **还没做的**：画面里的中文（营业执照、申诉页面、二手平台等）仍是中文，只有片尾换成了英文。

## 文件

| 文件 | 作用 |
|---|---|
| `translation.json` | 192 条英文译稿。`c` 指向 `数据/chN.js` 里的中文字幕分块范围；`say` 是 TTS 读法，用于年份、状态码等 |
| `make_subs.py` | 生成全片时间的 SRT，并检查覆盖和语速。`en.srt`/`zh.srt` 对应原成片，`en-nosub.srt`/`zh-nosub.srt` 对应无字幕版 |
| `tts_gen.py` | 逐句生成英文旁白，支持 Kokoro（本地）、Amazon Polly、MiniMax、OpenRouter。Kokoro 读不准的人名音标写在 `PHONEMES` 里 |
| `tts_lines.tsv` | TTS 逐句清单：id、起点、可用秒数、读法 |
| `dub.py` | `voice`：按中文起点摆放英文旁白；`mix`：和配乐层、片尾原声混成母带；`sample`：出试听样片 |
| `burn.py` | 出片：片尾替换（`--signs signs.json`），可选烧字幕，可选 H.265 编码 |
| `signs.json` | 片尾四页的英文替换：黑框位置、英文行、样式、淡入淡出帧 |
| `ocr_inventory.py` / `ocr_items.tsv` | 全片画面中文的 OCR 盘点（每秒 1 帧），给以后翻译画面文字用 |
| `setup.sh` | 准备环境：装依赖、下载无字幕原片并校验、重建配乐层、下载 Kokoro 模型和字体 |

## 做法要点

1. **按配音的要求翻译。**
   - 每条英文对应一段中文字幕分块，句长按每秒 2.5–2.8 词控制。`make_subs.py` 会列出过快的句子。
   - 画面卡点的关键词保持在同一时刻，比如"要有光"逐项补参数、Approve、黑洞、403/429/402。
   - 原本就是英文产品文案的笑点，用回英文原话：usage limit、bypass permissions、suspicious signals、`/compact` 等。
2. **对时间。** 无字幕版和原成片之间的偏移，是用重建的配乐层和视频音轨做互相关测出来的：全片 13 处一致，都是 3.0426 秒。这也顺带验证了 `声音/` 的脚本能逐采样重建成片的声音层。
3. **配音。**
   - 逐句生成，每句放在对应中文的起点。
   - 放不下时，先最多提前 0.25 秒起读，再最多加速到 1.12 倍；仍放不下就顺延下一句并报告，这种句子应该回 `translation.json` 改短。
   - 全部 192 句都用 Whisper 反向转写，和原稿比对检查读音。
4. **片尾。** 用 OCR 定位每行字，用逐帧亮度测出淡入淡出的起止帧。先用不透明黑框盖住中文（黑底上看不出），再按原位置、原颜色画英文。

## 复现

需要：Python 3.11 以上、ffmpeg（带 libass、libx265），约 3 GB 空闲磁盘。

```bash
bash 英文版/setup.sh          # 无字幕原片地址可用 NOSUB_URL、NOSUB_SHA256 覆盖
cd 英文版
python make_subs.py --offset 3.0426 --suffix nosub && python dub.py lines
KOKORO_DIR=$PWD/kokoro python tts_gen.py kokoro am_michael        # 192 句，CPU 约 4 分钟
python dub.py voice --tts tts/kokoro-am_michael
python dub.py mix /home/user/media/nosub.mp4 --offset 3.0426
python burn.py /home/user/media/nosub.mp4 out.mp4 --offset 3.0426 --no-mask --no-subs \
  --signs signs.json --audio mix_en.wav --hevc
```

`--offset 3.0426` 只适用于这个无字幕原片。换成别的版本，要重新测偏移：用 `声音/full-music.wav` 和该视频的音轨做互相关。

## 已知问题

- **画面中文未翻译。** 要渲染成英文，最好的办法是改镜头源码重新渲染，但仓库里只有 4 个镜头的源码，后期的逐字时钟重映射、颗粒、调色脚本也不在仓库里。退而求其次，只能在现有视频上逐处覆盖替换。
- **对齐偏差。** 第五章"humanity's access to the universe has been suspended"一句比画面晚约 0.5 秒，其余句子都在 0.2 秒以内。

## 协议

- 脚本（`.py`、`.sh`）：MIT。
- 英文译稿、字幕和画面文字的英文（`translation.json`、`*.srt`、`tts_lines.tsv`、`signs.json`、`ocr_items.tsv`）：属于作品内容的改编，CC BY-NC-SA 4.0。
- 本说明：CC BY 4.0。

详见根目录的 [LICENSE.md](../LICENSE.md)。
