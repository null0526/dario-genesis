#!/usr/bin/env bash
# 英文版环境准备。在仓库根目录运行：bash 英文版/setup.sh
#   1. 建独立虚拟环境 英文版/.venv，按 requirements.txt 装固定版本的依赖
#   2. 下载并校验：无字幕原片、Kokoro 模型和音色、片尾字体（都固定版本，逐个校验 SHA-256）
#   3. 用 声音/ 的脚本重建配乐层 full-music.wav。中间产物留在 声音/（约 3 GB，已被 .gitignore 忽略），不会删除任何已有文件
# 目录可用环境变量覆盖：MEDIA、KOKORO_DIR、FONT_DIR、VENV。无字幕原片可用 NOSUB_URL 换地址，NOSUB_SHA256 换校验值（设为空则不校验）。
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
EN="$ROOT/英文版"
MEDIA=${MEDIA:-$EN/media}
KOKORO_DIR=${KOKORO_DIR:-$EN/kokoro}
FONT_DIR=${FONT_DIR:-$EN/fonts}
VENV=${VENV:-$EN/.venv}
mkdir -p "$MEDIA" "$KOKORO_DIR" "$FONT_DIR"

# fetch 地址 目标 SHA256：目标已存在且校验通过就跳过；否则下载到临时文件（HTTP 出错即失败），校验通过后才改成正式文件名
fetch() {
  local url=$1 dest=$2 sha=$3 tmp
  if [ -f "$dest" ] && { [ -z "$sha" ] || echo "$sha  $dest" | sha256sum -c --status -; }; then echo "已就绪：$(basename "$dest")"; return; fi
  tmp=$(mktemp "$dest.part.XXXXXX")
  if ! curl -fsSL --retry 3 --retry-delay 2 -o "$tmp" "$url"; then rm -f "$tmp"; echo "下载失败：$url" >&2; return 1; fi
  if [ -n "$sha" ] && ! echo "$sha  $tmp" | sha256sum -c --status -; then rm -f "$tmp"; echo "校验失败：$url" >&2; return 1; fi
  mv -f "$tmp" "$dest"; echo "已下载：$(basename "$dest")"
}

# 1. Python 依赖
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q -r "$EN/requirements.txt"
PY="$VENV/bin/python"

# 2. 下载
# 无字幕原片：原仓库 v1.0 Release。它比原成片时间轴晚 3.0426 秒，所以后续命令都带 --offset 3.0426
fetch "${NOSUB_URL:-https://github.com/null0526/dario-genesis/releases/download/v1.0/dario-genesis-nosub-1080p.mp4}" \
      "$MEDIA/nosub.mp4" "${NOSUB_SHA256-1b0c215b83ff60854bb0ede13ffe9d3ab07f161124cd06c6bddfca478c2b6fcd}"
# Kokoro-82M ONNX（Apache-2.0），固定在 onnx-community/Kokoro-82M-v1.0-ONNX 的 commit 1939ad2a
HF=https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/1939ad2a8e416c0acfeecc08a694d14ef25f2231
fetch "$HF/onnx/model.onnx"        "$KOKORO_DIR/model.onnx"     8fbea51ea711f2af382e88c833d9e288c6dc82ce5e98421ea61c058ce21a34cb
fetch "$HF/voices/am_michael.bin"  "$KOKORO_DIR/am_michael.bin" 1d1f21dd8da39c30705cd4c75d039d265e9bc4a2a93ed09bc9e1b1225eb95ba1
# Source Serif 4（SIL OFL 1.1），片尾英文用；固定在 adobe-fonts/source-serif 的 4.005R
FONTS=https://cdn.jsdelivr.net/gh/adobe-fonts/source-serif@4.005R/TTF
fetch "$FONTS/SourceSerif4-Regular.ttf" "$FONT_DIR/SourceSerif4-Regular.ttf" e5a4ee6a3d87bb9024796be390c6771e2a0eb1883dae25effaf57ca01668e24b
fetch "$FONTS/SourceSerif4-Light.ttf"   "$FONT_DIR/SourceSerif4-Light.ttf"   3051ab89b702d23474f0dccbc183b3004ff843f5c343d1ee31eca3d927fee0db

# 3. 配乐层（不含旁白），与成片逐采样一致。已有且大小正确（681.67 秒 48 kHz 立体声 float32）就不重建
MUSIC="$ROOT/声音/full-music.wav"
if [ ! -f "$MUSIC" ] || [ "$(stat -c %s "$MUSIC")" != 261760026 ]; then
  (cd "$ROOT/声音" && for f in ch1_seq ch1_part_a ch1_part_b splice_ch1 ch2_part_a ch2_part_b splice_ch2 ch3 ch4 ch5_part_a ch5_part_b splice_ch5 splice_all; do "$PY" "$f.py" > /dev/null; done)
fi

echo "就绪：$MEDIA/nosub.mp4、声音/full-music.wav、$KOKORO_DIR、$FONT_DIR；Python：$PY"
