# -*- coding: utf-8 -*-
from PIL import Image
img = Image.open('D:/project/sunny-multica-skills/docs/images/harness-architecture.png')
img.thumbnail((1400, 1300))
img.save('D:/project/sunny-multica-skills/docs/images/.gen/arch_review.png')
print(img.size)
