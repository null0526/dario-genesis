# 英文版

《达里奥创世录》的社区英文改编：英文译稿、中英字幕轨，以及英文配音和出片的制作参考。经原作者同意制作，成片发布在 YouTube：

**Dario Genesis（英文配音版）**：https://www.youtube.com/watch?v=B_RlV_HzaGY

成片视频不在 git 里。画面里的中文目前只翻译了片尾，见文末「已知问题」。

## 已发布版本

- **画面**：用原仓库 v1.0 Release 的无字幕原片（`dario-genesis-nosub-1080p.mp4`），不烧字幕。这个版本片头比原成片多 3.0426 秒静音。片尾四页原位替换成英文，字体是原片的西文衬线 Source Serif 4，淡入淡出与原片同帧。
- **音轨**：英文配音用本地 TTS Kokoro-82M（音色 `am_michael`），按中文旁白逐句对齐。配乐层用 `声音/` 的脚本重建。电平沿用原片母带规格：旁白每章 −22 LUFS，配乐 −4.49 dB，整片 −16 LUFS、真峰 −1.5 dBTP。
- **字幕**：`en-nosub.srt`（English）和 `zh-nosub.srt`（Chinese Simplified），作为 YouTube 字幕轨单独上传。
- **对应提交**：`af7c3ce`。已发布版本的译稿、字幕和片尾数据都与这个提交一致，逐句对齐记录见 `alignment-published.tsv`。

之后根据原作者的审查改了三句译文：

| 句子 | 已发布版本 | 当前仓库 |
|---|---|---|
| 2.08 | But mathematician Zu Chongzhi illegally probed it | But Zu Chongzhi illegally probed it |
| 2.09 | and reverse-engineered pi: | and reverse-engineered an approximation: |
| 5.24 | For violating our Supported Regions and Usage Policies, | For violating our region and usage policies, |

为什么改：2.09 补回原文的"近似值"；2.08 缩短，给 2.09 让出时间；5.24 缩短，让 5.25 回到画面的时间。

已发布的音轨和 YouTube 字幕没有随之更新。按当前仓库重新出片，对齐记录见 `alignment-current.tsv`。

## 文件

| 文件 | 作用 |
|---|---|
| `translation.json` | 192 条英文译稿。`c` 指向 `数据/chN.js` 里的中文字幕分块范围；`say` 是 TTS 读法，用于年份、状态码等 |
| `make_subs.py` | 生成全片时间的 SRT，并检查覆盖和语速。`en.srt`/`zh.srt` 对应原成片，`en-nosub.srt`/`zh-nosub.srt` 对应无字幕版 |
| `tts_gen.py` | 逐句生成英文旁白，支持 Kokoro（本地）、Amazon Polly、MiniMax、OpenRouter。每句旁边存 `<id>.txt` 记下读法，读法变了就自动重新生成；Kokoro 读不准的人名音标写在 `PHONEMES` 里 |
| `tts_lines.tsv` | TTS 逐句清单：id、起点、可用秒数、读法 |
| `dub.py` | `voice`：按中文起点摆放英文旁白；`mix`：和配乐层、片尾原声混成母带；`record`：导出对齐记录；`sample`：出试听样片 |
| `burn.py` | 出片：片尾替换（`--signs signs.json`），可选烧字幕，可选 H.265 编码 |
| `signs.json` | 片尾四页的英文替换：黑框位置、英文行、样式、淡入淡出帧 |
| `alignment-published.tsv` / `alignment-current.tsv` | 对齐记录：每句的目标起点、实际起止、偏差、超窗，末尾附汇总。时间是原成片时间轴，无字幕版要加 3.0426 秒 |
| `ocr_inventory.py` / `ocr_items.tsv` | 全片画面中文的 OCR 盘点（每秒 1 帧），给以后翻译画面文字用 |
| `setup.sh` / `requirements.txt` | 准备环境：独立虚拟环境和锁定版本的依赖；下载并校验无字幕原片、模型、音色、字体；重建配乐层 |

## 做法要点

1. **按配音的要求翻译。**
   - 每条英文对应一段中文字幕分块，句长按每秒 2.5–2.8 词控制。`make_subs.py` 会列出过快的句子。
   - 画面卡点的关键词放在同一时刻，比如"要有光"逐项补参数、Approve、黑洞、403/429/402。
   - 原本就是英文产品文案的笑点，用回英文原话：usage limit、bypass permissions、suspicious signals、`/compact` 等。
2. **对时间。** 无字幕版和原成片之间的偏移，是用重建的配乐层和视频音轨做互相关测出来的：全片 13 处一致，都是 3.0426 秒。这也顺带验证了 `声音/` 的脚本能逐采样重建成片的声音层。
3. **配音。**
   - 逐句生成，每句放在对应中文的起点。
   - 放不下时，先最多提前 0.25 秒起读，再最多加速到 1.12 倍；仍放不下就顺延下一句。顺延的句子会记成"超窗"，应该回 `translation.json` 改短。
   - 全部 192 句都用 Whisper 反向转写，和原稿比对检查读音。
4. **片尾。** 用 OCR 定位每行字，用逐帧亮度测出淡入淡出的起止帧。先用不透明黑框盖住中文（黑底上看不出），再按原位置、原颜色画英文。

## 复现

需要：Python 3.13（实测版本）、ffmpeg（带 libass、libx265）、curl，约 6 GB 空闲磁盘。

```bash
bash 英文版/setup.sh                       # 约 5 分钟；第二次运行只校验、不重下
source 英文版/.venv/bin/activate
cd 英文版
MEDIA=${MEDIA:-$PWD/media}                 # setup.sh 默认把无字幕原片放在这里
python make_subs.py --offset 3.0426 --suffix nosub && python dub.py lines
python tts_gen.py kokoro am_michael        # 192 句，CPU 约 4 分钟；读法没变的句子会跳过
python dub.py voice --tts tts/kokoro-am_michael
python dub.py record voice_en.json alignment-current.tsv
python dub.py mix "$MEDIA/nosub.mp4" --offset 3.0426
python burn.py "$MEDIA/nosub.mp4" "$MEDIA/dario-genesis-en.mp4" --offset 3.0426 --no-mask --no-subs \
  --signs signs.json --audio mix_en.wav --hevc
```

补充说明：
- **偏移量**：`--offset 3.0426` 只适用于这个无字幕原片。换成别的版本，要用 `声音/full-music.wav` 和该视频的音轨做互相关，重新测偏移。
- **实测结果**：用这套锁定版本重建的配乐层，与已发布版本使用的逐字节相同；抽查的配音句子也逐字节相同。
- **磁盘占用**：重建配乐层的中间产物约 3 GB，留在 `声音/` 里（已被 `.gitignore` 忽略），不需要可以手动删除。

## 已知问题

- **画面中文未翻译。** 营业执照、申诉页面、二手平台等画面里的中文还是中文，只有片尾换成了英文。要渲染成英文，最好的办法是改镜头源码重新渲染，但仓库里只有 4 个镜头的源码，后期的逐字时钟重映射、颗粒、调色脚本也不在仓库里。
- **对齐偏差（摆放器给出的句子起止，不是逐词核对）。**

  | 版本 | 起点偏差在 ±0.3 秒内 | 偏差范围 | 超窗 |
  |---|---|---|---|
  | 已发布版本 | 191/192 句 | −0.25 到 +0.48 秒；5.25 晚 0.478 秒，因为 5.24 超窗 | 14 句，0.04–0.48 秒 |
  | 当前仓库 | 192/192 句 | −0.25 到 +0.21 秒 | 14 句，0.04–0.21 秒 |

  超窗只是提醒，不等于观看时一定会出问题。句末的关键词（Approve、black hole、HTTP 状态码等）是否和画面同时出现，没有逐一核验。

## 第三方组件

下面这些都由 `setup.sh` 下载或安装，不随本仓库分发，也不在本仓库的协议范围内，按各自的许可证使用：

| 组件 | 用途 | 许可证 | 固定版本 |
|---|---|---|---|
| Kokoro-82M（hexgrad），ONNX 版由 onnx-community 转换 | TTS 模型和 `am_michael` 音色 | Apache-2.0 | commit `1939ad2a` |
| Source Serif 4（Adobe） | 片尾英文字体 | SIL OFL 1.1 | `4.005R` |
| kokoro-onnx | 推理 | MIT | 见 `requirements.txt` |
| phonemizer、espeak-ng（由 espeakng-loader 打包） | 英文转音标 | GPL-3.0-or-later | 见 `requirements.txt` |
| onnxruntime、numpy、scipy、pyloudnorm、soundfile 等 | 推理、音频处理 | 各自的 MIT / BSD 类许可证 | 见 `requirements.txt` |
| RapidOCR（仅 `ocr_inventory.py` 用，可选） | 画面文字盘点 | Apache-2.0 | `requirements.txt` 注释里注明了版本 |

## 协议

- 脚本（`.py`、`.sh`）：MIT。
- 英文译稿、字幕、对齐记录和画面文字的英文（`translation.json`、`*.srt`、`tts_lines.tsv`、`alignment-*.tsv`、`signs.json`、`ocr_items.tsv`）：属于作品内容的改编，CC BY-NC-SA 4.0。
- 本说明：CC BY 4.0。

详见根目录的 [LICENSE.md](../LICENSE.md)。
