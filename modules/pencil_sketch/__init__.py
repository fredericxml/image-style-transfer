import cv2
import numpy as np
from utilities import base_path, base64_uri_from_array


background_image_path = base_path('modules', 'pencil_sketch', 'shading-background.jpg')
sketch_bg = cv2.imread(background_image_path, cv2.CV_8UC1)


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


def sharpen(img: np.ndarray, sharpen_factor) -> np.ndarray:
    """Sharpen image by defined kernel size
    Args:
        image: (np.ndarray) - image to be sharpened
    Returns:
        image: (np.ndarray) - sharpened image
    """
    inverted = 255 - img
    kernel = np.array([[0, -1, 0], [-1, sharpen_factor, -1], [0, -1, 0]])
    return 255 - cv2.filter2D(src=inverted, ddepth=-1, kernel=kernel)


def make_sketch(file, sharpen_factor):
    image = cv2.imdecode(np.frombuffer(file, np.uint8), cv2.IMREAD_COLOR)
    bg = cv2.resize(sketch_bg, (image.shape[1], image.shape[0]))

    grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_image = cv2.GaussianBlur(255 - grey_image, (101, 101), 2)
    image = dodge(blur_image, grey_image)

    if sharpen_factor is not None:
        image = sharpen(image, sharpen_factor)

    image = cv2.multiply(image, bg, scale=1/255)

    return base64_uri_from_array(image)