# -*- coding: utf-8 -*-
from PIL import Image
for name in ['orchestration-signal', 'sdd-pipeline', 'tdd-microloop']:
    img = Image.open(f'D:/project/sunny-multica-skills/docs/images/{name}.png')
    img.thumbnail((1200, 1200))
    img.save(f'D:/project/sunny-multica-skills/docs/images/.gen/{name.split("-")[0]}_review.png')
    print(name, img.size)
