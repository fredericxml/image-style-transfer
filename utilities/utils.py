import base64
import os

import cv2
import psutil

from config import BASE_PATH


def base_path(*args):
    return os.path.join(BASE_PATH, *args)


def base64_uri_from_array(image_array):
    success, encoded = cv2.imencode('.png', image_array)
    if not success:
        raise RuntimeError('Could not encode output image.')
    return 'data:image/png;base64,' + base64.b64encode(encoded).decode('ascii')


def optimize_image_size(original_size):
    height, width = map(int, original_size)
    scale = min(1.0, 350 / max(height, width))
    return [max(1, int(height * scale)), max(1, int(width * scale))]


def print_current_memory_usage(description=''):
    memory = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
    print(f'{description}: {memory:.2f} MiB')
