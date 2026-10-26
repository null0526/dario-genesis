#!/usr/bin/env bash
# 英文版环境准备：装依赖、下载无字幕原片并校验、重建配乐层、下载 Kokoro 模型和字体。约 5 分钟。
# 用法：bash 英文版/setup.sh   （在仓库根目录）
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
MEDIA=${MEDIA:-/home/user/media}
mkdir -p "$MEDIA"

pip install -q numpy scipy pyloudnorm boto3 kokoro-onnx soundfile rapidocr_onnxruntime

# 无字幕原片（默认取 usernameistony/dario-genesis 的 Release v0.1；它比原成片时间轴晚 3.0426 秒）
# 换别的文件：设 NOSUB_URL；校验值对不上时设 NOSUB_SHA256（设为空则不校验）
NOSUB_URL=${NOSUB_URL:-https://github.com/usernameistony/dario-genesis/releases/download/v0.1/dario-genesis-nosub-1080p.mp4}
NOSUB_SHA256=${NOSUB_SHA256-1b0c215b83ff60854bb0ede13ffe9d3ab07f161124cd06c6bddfca478c2b6fcd}
[ -f "$MEDIA/nosub.mp4" ] || curl -sS -L -o "$MEDIA/nosub.mp4" "$NOSUB_URL"
[ -z "$NOSUB_SHA256" ] || echo "$NOSUB_SHA256  $MEDIA/nosub.mp4" | sha256sum -c -

# 配乐层（不含旁白），与成片逐采样一致
if [ ! -f "$ROOT/声音/full-music.wav" ]; then
  (cd "$ROOT/声音" && for f in ch1_seq ch1_part_a ch1_part_b splice_ch1 ch2_part_a ch2_part_b splice_ch2 ch3 ch4 ch5_part_a ch5_part_b splice_ch5 splice_all; do python3 $f.py > /dev/null; done
   find . -maxdepth 1 -name '*.wav' ! -name 'full-music.wav' -delete)
fi

# Kokoro（本地免费 TTS）
K=${KOKORO_DIR:-$ROOT/英文版/kokoro}; mkdir -p "$K"
B=https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main
[ -f "$K/model.onnx" ] || curl -sS -L -o "$K/model.onnx" $B/onnx/model.onnx
for v in bm_george am_michael af_heart; do [ -f "$K/$v.bin" ] || curl -sS -L -o "$K/$v.bin" $B/voices/$v.bin; done

# 片尾英文用的 Source Serif 4（原片西文衬线，SIL OFL）
mkdir -p ~/.fonts
for f in SourceSerif4-Regular.ttf SourceSerif4-Light.ttf; do
  [ -f ~/.fonts/$f ] || curl -sS -L -o ~/.fonts/$f https://cdn.jsdelivr.net/gh/adobe-fonts/source-serif@release/TTF/$f
done
fc-cache -f > /dev/null

echo "就绪：$MEDIA/nosub.mp4、声音/full-music.wav、$K"
