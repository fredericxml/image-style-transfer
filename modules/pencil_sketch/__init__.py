import cv2
import numpy as np
from utilities.image_validation import decode_image
from utilities.utils import base_path, base64_uri_from_array, optimize_image_size


background_image_path = base_path('modules', 'pencil_sketch', 'shading-background.jpg')
sketch_bg = cv2.imread(background_image_path, cv2.IMREAD_GRAYSCALE)


def dodge(front: np.ndarray, back: np.ndarray) -> np.ndarray:
    """The formula comes from https://en.wikipedia.org/wiki/Blend_modes
    Args:
        front: (np.ndarray) - front image to be applied to dodge algorithm
        back: (np.ndarray) - back image to be applied to dodge algorithm
    Returns:
        image: (np.ndarray) - dodged image
    """
    denominator = 255.0 - front
    result = np.full(front.shape, 255.0)
    np.divide(back * 255.0, denominator, out=result, where=denominator != 0)
    result[back == 255] = 255
    return np.clip(result, 0, 255).astype(np.uint8)


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
    image = decode_image(file)
    if sketch_bg is None:
        raise RuntimeError('Sketch background asset is unavailable.')
    bg = cv2.resize(sketch_bg, (image.shape[1], image.shape[0]))

    grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_image = cv2.GaussianBlur(255 - grey_image, (101, 101), 2)
    image = dodge(blur_image, grey_image)

    if sharpen_factor is not None:
        image = sharpen(image, sharpen_factor)

    image = cv2.multiply(image, bg, scale=1/255)

    height, width = optimize_image_size(image.shape[:2])
    final_image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

    return {
        'image': base64_uri_from_array(final_image),
        'dimension': f'{image.shape[0]}x{image.shape[1]}'
    }
