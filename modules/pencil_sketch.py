import base64

import cv2
import numpy as np


sketch_bg = cv2.imread('static/img/pencil-sketch-bg.jpg', cv2.CV_8UC1)
current_state = {'bg': None, 'img': None}


def reset_current_state():
    global current_state
    current_state = {'bg': None, 'img': None}


def make_sketch(file, sharpen_value=None):
    global current_state

    if current_state['img'] is None:
        img = cv2.imdecode(np.fromstring(file, np.uint8), cv2.IMREAD_UNCHANGED)
        bg = cv2.resize(sketch_bg, (img.shape[1], img.shape[0]))

        grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur_img = cv2.GaussianBlur(255 - grey_img, (101, 101), 2)
        img = dodge(blur_img, grey_img)

        current_state = {'bg': bg, 'img': img}
    else:
        bg = current_state['bg']
        img = current_state['img']

    img = sharpen(img, sharpen_value)
    img = cv2.multiply(img, bg, scale=1/256)

    return base64.b64encode(cv2.imencode('.png', img)[1]).decode()


def dodge(front: np.ndarray, back: np.ndarray) -> np.ndarray:
    """The formula comes from https://en.wikipedia.org/wiki/Blend_modes
    Args:
        front: (np.ndarray) - front image to be applied to dodge algorithm
        back: (np.ndarray) - back image to be applied to dodge algorithm
    Returns:
        image: (np.ndarray) - dodged image
    """
    result = back*255.0 / (255.0-front)
    result[result > 255] = 255
    result[back == 255] = 255
    return result.astype('uint8')


def sharpen(img: np.ndarray, sharpen_value=None) -> np.ndarray:
    """Sharpen image by defined kernel size
    Args:
        image: (np.ndarray) - image to be sharpened
    Returns:
        image: (np.ndarray) - sharpened image
    """
    if sharpen_value is not None and isinstance(sharpen_value, int):
        inverted = 255 - img
        kernel = np.array([[0, -1, 0], [-1, sharpen_value, -1], [0, -1, 0]])
        return 255 - cv2.filter2D(src=inverted, ddepth=-1, kernel=kernel)

    return img