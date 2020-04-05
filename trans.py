from PIL import Image
import numpy as np
import copy
from io import BytesIO
import base64
from cv2 import cv2

class transtool:
    
    def rgba2rgb(self,rgbaimg):
        return cv2.cvtColor(rgbaimg, cv2.COLOR_RGBA2RGB)

    def base64_to_rgb(self,base64img):
        imgdata = base64.b64decode(base64img)
        buffered = BytesIO()
        buffered.write(imgdata)
        rgbimg = self.rgba2rgb(np.array(Image.open(buffered)))
        return Image.fromarray(rgbimg)

    def img2base64(self,img):
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_str