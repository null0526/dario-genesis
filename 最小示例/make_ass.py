import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, "timeline.json"), encoding="utf-8"))
S = {s["id"]: s for s in TL["segments"]}
T_AB = S["S04"]["end"] + 0.45; T_BC = S["S05"]["end"] + 0.30


def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Ink,Noto Sans SC,62,&H001C2226,&H001C2226,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,2,100,100,60,1
Style: Light,Noto Sans SC,62,&H00DFE6E9,&H00DFE6E9,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,2,100,100,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
lines = [head]
for s in TL["segments"]:
    for c in s["chunks"]:
        style = "Light" if T_AB <= c["start"] < T_BC else "Ink"
        txt = c["text"].rstrip("，。")
        lines.append(f"Dialogue: 0,{ts(c['start'])},{ts(c['end'] - 0.05)},{style},,0,0,0,,{txt}\n")
open(os.path.join(HERE, "subs.ass"), "w", encoding="utf-8", newline="").write("".join(lines))
print("ok")
