# -*- coding: utf-8 -*-
"""Chrome headless 截图导出 PNG（处理 CJK + 窗口裁剪）"""
import subprocess, sys, os
from PIL import Image

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
IMGDIR = r"D:\project\sunny-multica-skills\docs\images"

def export(name, w, h, scale=2):
    svg = open(os.path.join(IMGDIR, f'{name}.svg'), encoding='utf-8').read()
    html = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
body {{ margin:0; padding:0; background:#ffffff; }}</style></head>
<body>{svg}</body></html>'''
    hpath = os.path.join(IMGDIR, f'.gen\\{name}.html')
    with open(hpath, 'w', encoding='utf-8') as f:
        f.write(html)
    png = os.path.join(IMGDIR, f'.gen\\{name}_raw.png')
    win_w, win_h = int(w * 1.3), int(h * 1.3)
    import tempfile, shutil
    profile = tempfile.mkdtemp(prefix='chrome-svg-')
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                        '--user-data-dir=' + profile,
                        f'--force-device-scale-factor={scale}', f'--window-size={win_w},{win_h}',
                        f'--screenshot={png}', f'file:///{hpath.replace(chr(92), "/")}'],
                       capture_output=True, timeout=120)
    shutil.rmtree(profile, ignore_errors=True)
    import time
    for _ in range(20):
        if os.path.exists(png):
            try:
                img = Image.open(png); img.verify()
                break
            except Exception:
                pass
        time.sleep(0.5)
    if not os.path.exists(png):
        print('chrome rc=', r.returncode)
        print(r.stderr.decode('utf-8', 'replace')[:2000])
        raise SystemExit('screenshot not produced')
    img = Image.open(png)
    img.crop((0, 0, w * scale, h * scale)).save(os.path.join(IMGDIR, f'{name}.png'))
    os.remove(png)
    print(f'{name}.png -> {w*scale}x{h*scale}')

if __name__ == '__main__':
    export(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
