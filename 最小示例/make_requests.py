import json, os, re
from script import SEGS
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(here, "tts"), exist_ok=True)
tot = 0
for sid, text in SEGS:
    req = {"model": "minimax/speech-2.8-hd", "voice": "doc_commentary", "input": text, "response_format": "mp3"}
    with open(os.path.join(here, "tts", f"{sid}-request.json"), "w", encoding="utf-8", newline="") as f:
        json.dump(req, f, ensure_ascii=False, indent=2)
    n = len(re.findall(r"[一-鿿]", text))
    tot += n
    print(sid, n)
print("total han chars", tot)
