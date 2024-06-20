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


# def backup(file):
#     response = requests.post('https://freeimage.host/api/1/upload', data={
#         'key': '6d207e02198a847aa98d0a2a901485a5',
#         'action': 'upload',
#         'source': base64.b64encode(file)
#     }).json()

#     url = response['image']['url']
#     response = requests.get(url, stream=True)
#     img = Image.open(response.raw)
#     buffered = io.BytesIO()
#     img.save(buffered, format='PNG')
#     pngImageB64String = 'data:image/png;base64,'
#     pngImageB64String += base64.b64encode(buffered.getvalue()).decode('utf8')