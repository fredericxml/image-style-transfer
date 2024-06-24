import cv2
import numpy as np
import tensorflow as tf
from utilities.utils import base_path, base64_uri_from_array


# https://www.kaggle.com/models/spsayakpaul/cartoongan
model_path = base_path('models', 'cartoongan_dr.tflite')
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()


def load_image(image_buffer):
    image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image = image.astype(np.float32) / 127.5 - 1
    image = np.expand_dims(image, 0)
    image = tf.convert_to_tensor(image)
    return image


# Function to pre-process by resizing an central cropping it
def preprocess_image(image, target_size):
    # Resize the image so that the shorter dimension becomes the target dim
    shape = tf.cast(tf.shape(image)[1:-1], tf.float32)
    short_dim = min(shape)
    scale = target_size / short_dim
    new_shape = tf.cast(shape * scale, tf.int32)
    image = tf.image.resize(image, new_shape)
    image = tf.image.resize(image, [target_size, target_size])
    return image


def postprocess_image(raw_prediction, target_size):
    image = tf.image.resize(raw_prediction, target_size)
    image = (np.squeeze(image) + 1.0) * 127.5
    image = np.clip(image, 0, 255).astype(np.uint8)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def make_cartoon(file):
    source_image = load_image(file)
    preprocessed_source_image = preprocess_image(source_image, 512)

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], preprocessed_source_image)
    interpreter.invoke()

    raw_output = interpreter.tensor(output_details[0]['index'])()
    final_output = postprocess_image(raw_output, source_image.shape[1:3])

    return {
        'image': base64_uri_from_array(final_output),
        'dimension': f'{source_image.shape[1]}x{source_image.shape[2]}'
    }