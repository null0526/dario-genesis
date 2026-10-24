"""渲染：Chrome(本机) + Playwright 逐帧抓取 canvas JPEG -> ffmpeg 编码为无字幕、无声的 silent.mp4
用法: render.py stills t1,t2,...   |  render.py video [起帧 止帧]"""
import sys, os, json, base64, subprocess
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = os.environ.get("CHROME_PATH")   # 不设则用 Playwright 自带的 Chromium（playwright install chromium）
FPS = 30

# timeline.json -> timeline.js
tl = json.load(open(os.path.join(HERE, "timeline.json"), encoding="utf-8"))
open(os.path.join(HERE, "timeline.js"), "w", encoding="utf-8", newline="").write("window.TL=" + json.dumps(tl, ensure_ascii=False) + ";")


def open_page(p):
    b = p.chromium.launch(executable_path=CHROME, headless=True, args=["--allow-file-access-from-files"])
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    msgs = []
    pg.on("console", lambda m: msgs.append(m.text))
    pg.on("pageerror", lambda e: msgs.append("PAGEERROR " + str(e)))
    pg.goto("file:///" + os.path.join(HERE, "shot.html").replace("\\", "/"))
    pg.evaluate("window.ready")
    return b, pg, msgs


def main():
    mode = sys.argv[1]
    with sync_playwright() as p:
        b, pg, msgs = open_page(p)
        if mode == "stills":
            os.makedirs(os.path.join(HERE, "stills"), exist_ok=True)
            for t in [float(x) for x in sys.argv[2].split(",")]:
                d = pg.evaluate(f"grab({round(t*FPS)})")
                open(os.path.join(HERE, "stills", f"t{t:06.2f}.jpg"), "wb").write(base64.b64decode(d))
        else:
            n = int(pg.evaluate("Math.ceil(DUR*30)"))
            a = int(sys.argv[2]) if len(sys.argv) > 2 else 0
            z = int(sys.argv[3]) if len(sys.argv) > 3 else n
            out = os.path.join(HERE, "silent.mp4" if len(sys.argv) <= 2 else "silent-part.mp4")
            ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                                   "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
                                   "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-r", str(FPS), out],
                                  stdin=subprocess.PIPE)
            for i in range(a, z):
                ff.stdin.write(base64.b64decode(pg.evaluate(f"grab({i})")))
                if i % 150 == 0:
                    print("frame", i, "/", n, flush=True)
            ff.stdin.close(); ff.wait()
        print("console:", msgs[:10])
        b.close()


main()
