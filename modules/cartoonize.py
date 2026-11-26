import cv2
import numpy as np
import tensorflow as tf

from utilities.image_validation import decode_image
from utilities.utils import base_path, base64_uri_from_array, optimize_image_size

# https://www.kaggle.com/models/spsayakpaul/cartoongan
model_path = base_path('models', 'cartoongan_dr.tflite')


def load_image(image_buffer):
    image = cv2.cvtColor(decode_image(image_buffer), cv2.COLOR_BGR2RGB)
    image = image.astype(np.float32) / 127.5 - 1
    return tf.convert_to_tensor(np.expand_dims(image, 0))


def preprocess_image(image, target_size):
    return tf.image.resize(image, [target_size, target_size])


def postprocess_image(raw_prediction, target_size):
    image = np.asarray(tf.image.resize(raw_prediction, optimize_image_size(target_size)))[0]
    image = np.clip((image + 1.0) * 127.5, 0, 255).astype(np.uint8)
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def make_cartoon(file):
    source_image = load_image(file)
    preprocessed = preprocess_image(source_image, 512)
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    interpreter.set_tensor(interpreter.get_input_details()[0]['index'], preprocessed)
    interpreter.invoke()
    raw_output = interpreter.get_tensor(interpreter.get_output_details()[0]['index'])
    final_output = postprocess_image(raw_output, source_image.shape[1:3])
    return {'image': base64_uri_from_array(final_output),
            'dimension': f'{source_image.shape[1]}x{source_image.shape[2]}'}
