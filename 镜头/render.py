"""把一个镜头页面逐帧渲染成静帧联系表或无声视频。

用法（在本目录下）：
    python render.py 02-祖冲之割圆 stills            # 抽几帧，拼成 <镜头>/keyframes.jpg
    python render.py 02-祖冲之割圆 stills --frames 0,300,600
    python render.py 03-黑洞与回信 video --sub 8      # 输出 <镜头>/silent.mp4

页面协议：shot.html 在准备好后设 window.ready=true，提供 window.FRAMES（总帧数）和
window.grab(i)（返回第 i 帧 1920x1080 RGBA 的 base64）。WebGL 镜头读出来的像素是上下颠倒的，这里统一翻正。
--sub 是每帧的子帧数（运动模糊采样），成片用 8；试看时用 1–2 快很多。
旁白音频不在仓库里，所以只出无声视频；旁白文稿和逐字时码在 ../数据/。
"""
import argparse, asyncio, base64, os, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageDraw
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
W, H, FPS = 1920, 1080, 30
CHROME = os.environ.get('CHROME_PATH')   # 不设则用 Playwright 自带的 Chromium
sys.stdout.reconfigure(encoding='utf-8')


async def main(a):
    shot = HERE / a.shot
    start = time.monotonic(); errors = []; ff = None
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(executable_path=CHROME, headless=True,
                                           args=['--allow-file-access-from-files', '--ignore-gpu-blocklist', '--enable-gpu'])
        try:
            page = await browser.new_page(viewport={'width': W, 'height': H})
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: print('console:', m.text, flush=True) if m.type in ('error', 'warning') else None)
            await page.goto((shot / 'shot.html').as_uri() + f'?w={W}&h={H}&sub={a.sub}&seg=a')
            await page.wait_for_function('window.ready===true', timeout=180000)
            assert not errors, errors
            info = await page.evaluate('''()=>{
                let g=null, renderer='canvas2d';
                try{ g=(typeof gl!=='undefined'&&gl&&gl.getExtension)?gl:null; }catch(e){}
                if(g){ const d=g.getExtension('WEBGL_debug_renderer_info'); renderer=d?g.getParameter(d.UNMASKED_RENDERER_WEBGL):'webgl'; }
                return {renderer, webgl: !!g, frames: window.FRAMES};
            }''')
            print('renderer:', info['renderer'], 'frames:', info['frames'], flush=True)
            if 'SwiftShader' in info['renderer']:
                print('提示：浏览器在用软件渲染（SwiftShader），WebGL 镜头会很慢。', flush=True)
            flip = info['webgl']

            async def grab(i):
                raw = base64.b64decode(await page.evaluate('(i)=>window.grab(i)', i))
                assert len(raw) == W * H * 4 and not errors, errors
                return raw

            if a.mode == 'stills':
                n = info['frames']
                idx = [int(x) for x in a.frames.split(',')] if a.frames else [round(n * k / 8) for k in range(8)]
                cols, cw, ch = 2, 960, 540
                sheet = Image.new('RGB', (cw * cols, (ch + 26) * ((len(idx) + cols - 1) // cols)), '#111')
                pen = ImageDraw.Draw(sheet)
                for k, i in enumerate(idx):
                    im = Image.frombytes('RGBA', (W, H), await grab(i))
                    if flip: im = im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                    im = im.convert('RGB')
                    x = k % cols * cw; y = k // cols * (ch + 26)
                    sheet.paste(im.resize((cw, ch), Image.LANCZOS), (x, y + 26))
                    pen.text((x + 8, y + 6), f'{i / FPS:.3f}s / frame {i}', fill='white')
                    print('still', i, f'{time.monotonic() - start:.1f}s', flush=True)
                sheet.save(shot / 'keyframes.jpg', quality=92)
            else:
                vf = ['-vf', 'vflip'] if flip else []
                ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                       *vf, '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                                       str(shot / 'silent.mp4')], stdin=subprocess.PIPE)
                for i in range(info['frames']):
                    ff.stdin.write(await grab(i))
                    if i % 60 == 0: print(f'{i}/{info["frames"]} {time.monotonic() - start:.1f}s', flush=True)
                ff.stdin.close(); assert ff.wait(timeout=120) == 0; ff = None
        finally:
            if ff is not None:
                if ff.stdin and not ff.stdin.closed: ff.stdin.close()
                if ff.poll() is None: ff.terminate(); ff.wait(timeout=10)
            await browser.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('shot', help='镜头目录名，例如 02-祖冲之割圆')
    p.add_argument('mode', choices=['stills', 'video'])
    p.add_argument('--sub', type=int, default=8)
    p.add_argument('--frames', default='')
    asyncio.run(main(p.parse_args()))
