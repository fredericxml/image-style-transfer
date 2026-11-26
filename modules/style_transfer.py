import cv2
import numpy as np
import tensorflow as tf

from utilities.image_validation import decode_image, style_template_path
from utilities.utils import base_path, base64_uri_from_array, optimize_image_size

# https://www.kaggle.com/models/spsayakpaul/arbitrary-image-stylization-inceptionv3
model_path_predict = base_path('models', 'style_transfer', 'inceptionv3-predict_int8.tflite')
model_path_transfer = base_path('models', 'style_transfer', 'inceptionv3-transfer_int8.tflite')


def load_image(image, from_style_template=False):
    if from_style_template:
        image = style_template_path(image).read_bytes()
    image = cv2.cvtColor(decode_image(image), cv2.COLOR_BGR2RGB)
    image = tf.image.convert_image_dtype(tf.convert_to_tensor(image), tf.float32)
    return image[tf.newaxis, :]


def preprocess_image(image, target_size):
    return tf.image.resize(image, [target_size, target_size])


def postprocess_image(raw_output, target_size):
    image = np.asarray(tf.image.resize(raw_output, optimize_image_size(target_size)))[0]
    image = np.clip(image * 255, 0, 255).astype(np.uint8)
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def run_style_predict(preprocessed_style_image):
    interpreter = tf.lite.Interpreter(model_path=model_path_predict)
    interpreter.allocate_tensors()
    interpreter.set_tensor(interpreter.get_input_details()[0]['index'], preprocessed_style_image)
    interpreter.invoke()
    return interpreter.get_tensor(interpreter.get_output_details()[0]['index'])


def run_style_transform(style_bottleneck, preprocessed_content_image):
    interpreter = tf.lite.Interpreter(model_path=model_path_transfer)
    inputs = {detail['name']: detail for detail in interpreter.get_input_details()}
    interpreter.resize_tensor_input(inputs['content_image']['index'], list(preprocessed_content_image.shape))
    interpreter.allocate_tensors()
    inputs = {detail['name']: detail for detail in interpreter.get_input_details()}
    interpreter.set_tensor(inputs['Conv/BiasAdd']['index'], style_bottleneck)
    interpreter.set_tensor(inputs['content_image']['index'], preprocessed_content_image)
    interpreter.invoke()
    return interpreter.get_tensor(interpreter.get_output_details()[0]['index'])


def do_style_transfer(content_image_file, style_image_input, from_style_template, content_blending_ratio=0):
    content_image = load_image(content_image_file)
    style_image = load_image(style_image_input, from_style_template)
    content = preprocess_image(content_image, 350)
    style = preprocess_image(style_image, 256)
    bottleneck = run_style_predict(style)
    if not 0 <= content_blending_ratio <= 1:
        raise ValueError('Content blending ratio must be between 0 and 1.')
    if content_blending_ratio > 0:
        content_bottleneck = run_style_predict(preprocess_image(content_image, 256))
        bottleneck = (content_blending_ratio * content_bottleneck +
                      (1 - content_blending_ratio) * bottleneck)
    stylized = run_style_transform(bottleneck, content)
    final_output = postprocess_image(stylized, content_image.shape[1:3])
    return {'image': base64_uri_from_array(final_output),
            'content_dimension': f'{content_image.shape[1]}x{content_image.shape[2]}',
            'style_dimension': f'{style_image.shape[1]}x{style_image.shape[2]}'}
