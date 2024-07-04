import gc
import cv2
import numpy as np
import tensorflow as tf
from utilities.utils import base_path, base64_uri_from_array, optimize_image_size


# https://www.kaggle.com/models/spsayakpaul/arbitrary-image-stylization-inceptionv3
model_path_predict = base_path('models', 'style_transfer', 'inceptionv3-predict_int8.tflite')
model_path_transfer = base_path('models', 'style_transfer', 'inceptionv3-transfer_int8.tflite')


def load_image(image, from_style_template=False):
    if from_style_template:
        path = base_path('models', 'style_transfer', 'images', image)
        image = cv2.imread(path)
    else:
        image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)

    if image.shape[-1] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = np.array(image)
        image = tf.convert_to_tensor(image)
        image = tf.image.convert_image_dtype(image, tf.float32)
        image = image[tf.newaxis, :]
        return image
    elif image.shape[-1] == 3:
        image = tf.convert_to_tensor(image)
        image = tf.image.convert_image_dtype(image, tf.float32)
        image = image[tf.newaxis, :]
        return image
    elif image.shape[-1] == 1:
        # raise Error('Grayscale images not supported! Please try with RGB or RGBA images.')
        print('Exception not thrown')

    return image


def preprocess_image(image, target_size):
    # Resize the image so that the shorter dimension becomes 256px.
    shape = tf.cast(tf.shape(image)[1:-1], tf.float32)
    short_dim = min(shape)
    scale = target_size / short_dim
    new_shape = tf.cast(shape * scale, tf.int32)
    image = tf.image.resize(image, new_shape)
    image = tf.image.resize(image, [target_size, target_size])
    return image


def postprocess_image(raw_output, target_size):
    target_size = optimize_image_size(target_size)
    image = tf.image.resize(raw_output, target_size)
    if len(image.shape) > 3:
        image = np.squeeze(image)    
    image = (image * 255).astype(np.uint8)
    return image


# Run style prediction on preprocessed style image
def run_style_predict(preprocessed_style_image):
    # Load the model
    interpreter = tf.lite.Interpreter(model_path=model_path_predict)

    # Set model input
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    interpreter.set_tensor(input_details[0]['index'], preprocessed_style_image)

    # Calculate style bottleneck
    interpreter.invoke()
    style_bottleneck = interpreter.tensor(interpreter.get_output_details()[0]['index'])()
    
    # Clean up
    del interpreter
    gc.collect()
    
    return style_bottleneck


# Run style transform on preprocessed style image
def run_style_transform(style_bottleneck, preprocessed_content_image):
    # Load the model
    interpreter = tf.lite.Interpreter(model_path=model_path_transfer)

    # Set model input
    content_image_size = 350
    input_details = interpreter.get_input_details()
    for index in range(len(input_details)):
        if input_details[index]['name'] == 'content_image':
            index = input_details[index]['index']
            interpreter.resize_tensor_input(index, [1, content_image_size, content_image_size, 3])
    interpreter.allocate_tensors()

    # Set model inputs
    for index in range(len(input_details)):
        if input_details[index]['name'] == 'Conv/BiasAdd':
            interpreter.set_tensor(input_details[index]['index'], style_bottleneck)
        elif input_details[index]['name'] == 'content_image':
            interpreter.set_tensor(input_details[index]['index'], preprocessed_content_image)
    interpreter.invoke()

    # Transform content image
    stylized_image = interpreter.tensor(interpreter.get_output_details()[0]['index'])()
    
    # Clean up
    del interpreter
    gc.collect()

    return stylized_image


def do_style_transfer(content_image_file, style_image_input, from_style_template):        
    content_image = load_image(content_image_file)
    style_image = load_image(style_image_input, from_style_template)
    
    preprocessed_content_image = preprocess_image(content_image, 350)
    preprocessed_style_image = preprocess_image(style_image, 256)

    # Calculate style bottleneck for the preprocessed style image
    style_bottleneck = run_style_predict(preprocessed_style_image)

    # Blend the style bottleneck of style image and content image
    content_blending_ratio = 0

    if content_blending_ratio > 0:
        # Calculate style bottleneck of the content image
        style_bottleneck_content = run_style_predict(preprocess_image(content_image, 256))
        style_bottleneck_blended = content_blending_ratio * style_bottleneck_content \
                                + (1 - content_blending_ratio) * style_bottleneck
    else:
        style_bottleneck_blended = style_bottleneck

    # Stylize the content image using the style bottleneck
    stylized_image = run_style_transform(style_bottleneck_blended, preprocessed_content_image)

    final_output = postprocess_image(stylized_image, content_image.shape[1:3])
    return {
        'image': base64_uri_from_array(final_output),
        'content_dimension': f'{content_image.shape[1]}x{content_image.shape[2]}',
        'style_dimension': f'{style_image.shape[1]}x{style_image.shape[2]}'
    }