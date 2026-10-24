#!/usr/bin/env bash
# 新会话接手英文版：装依赖、下载无字幕成片、重建配乐层、下载 Kokoro 模型。约 5 分钟。
# 用法：bash 英文版/setup.sh   （在仓库根目录）
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
MEDIA=${MEDIA:-/home/user/media}
mkdir -p "$MEDIA"

pip install -q numpy scipy pyloudnorm boto3 kokoro-onnx soundfile

# 无字幕成片（fork 的 Release v0.1；比原成片时间轴晚 3.0426 秒）
if [ ! -f "$MEDIA/nosub.mp4" ]; then
  curl -sS -L -o "$MEDIA/nosub.mp4" https://github.com/usernameistony/dario-genesis/releases/download/v0.1/dario-genesis-nosub-1080p.mp4
fi
echo "1b0c215b83ff60854bb0ede13ffe9d3ab07f161124cd06c6bddfca478c2b6fcd  $MEDIA/nosub.mp4" | sha256sum -c -

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

echo "就绪：$MEDIA/nosub.mp4、声音/full-music.wav、$K"
