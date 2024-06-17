import os
import base64

import cv2
from config import BASE_PATH



def base_path(*args):
    return os.path.join(BASE_PATH, *args)


def base64_uri_from_array(image_array):
    base64_string = base64.b64encode(cv2.imencode('.png', image_array)[1]).decode()
    base64_uri = f'data:image/png;base64,{base64_string}'
    return base64_uri