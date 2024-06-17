import cv2
import numpy as np
import tensorflow as tf
from utilities import base_path, base64_uri_from_array


# https://www.kaggle.com/models/spsayakpaul/arbitrary-image-stylization-inceptionv3
model_path_predict = base_path('models', 'style_transfer', 'inceptionv3-predict_int8.tflite')
model_path_transfer = base_path('models', 'style_transfer', 'inceptionv3-transfer_int8.tflite')


def preprocess_image(image, target_dim):
    # Resize the image so that the shorter dimension becomes 256px.
    shape = tf.cast(tf.shape(image)[1:-1], tf.float32)
    short_dim = min(shape)
    scale = target_dim / short_dim
    new_shape = tf.cast(shape * scale, tf.int32)
    image = tf.image.resize(image, new_shape)

    # Central crop the image.
    image = tf.image.resize_with_crop_or_pad(image, target_dim, target_dim)

    return image


def load_image(image_buffer, target_size):
    img = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), cv2.IMREAD_COLOR)

    if img.shape[-1] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.array(img)
        img = tf.convert_to_tensor(img)
        img = tf.image.convert_image_dtype(img, tf.float32)
        img = img[tf.newaxis, :]
        return img
    elif img.shape[-1] == 3:
        img = tf.convert_to_tensor(img)
        img = tf.image.convert_image_dtype(img, tf.float32)
        img = img[tf.newaxis, :]
        return img
    elif img.shape[-1] == 1:
        # raise Error('Grayscale images not supported! Please try with RGB or RGBA images.')
        print('Exception not thrown')

    return img


# Run style prediction on preprocessed style image
def run_style_predict(preprocessed_style_image):
    # Load the model
    interpreter = tf.lite.Interpreter(model_path=model_path_predict)

    # Set model input
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    interpreter.set_tensor(input_details[0]["index"], preprocessed_style_image)

    # Calculate style bottleneck
    interpreter.invoke()
    style_bottleneck = interpreter.tensor(interpreter.get_output_details()[0]["index"])()

    return style_bottleneck

# Run style transform on preprocessed style image
def run_style_transform(style_bottleneck, preprocessed_content_image):
    content_image_size=350
    # Load the model
    interpreter = tf.lite.Interpreter(model_path=model_path_transfer)

    # Set model input
    input_details = interpreter.get_input_details()
    for index in range(len(input_details)):
        if input_details[index]["name"]=='content_image':
            index = input_details[index]["index"]
            interpreter.resize_tensor_input(index, [1, content_image_size, content_image_size, 3])
    interpreter.allocate_tensors()

    # Set model inputs
    for index in range(len(input_details)):
        if input_details[index]["name"]=='Conv/BiasAdd':
            interpreter.set_tensor(input_details[index]["index"], style_bottleneck)
        elif input_details[index]["name"]=='content_image':
            interpreter.set_tensor(input_details[index]["index"], preprocessed_content_image)
    interpreter.invoke()

    # Transform content image
    stylized_image = interpreter.tensor(interpreter.get_output_details()[0]["index"])()

    return stylized_image

def do_style_transfer(content_image_file, style_image_file):        
    content_image = load_image(content_image_file, target_size=350)
    style_image = load_image(style_image_file, target_size=256)
    
    preprocessed_content_image = preprocess_image(content_image, 350)
    preprocessed_style_image = preprocess_image(style_image, 256)

    # Calculate style bottleneck for the preprocessed style image
    style_bottleneck = run_style_predict(preprocessed_style_image)
    print('Calculating style bottleneck...')
    # style_bottleneck = run_style_predict(style_image)
    print('Style Bottleneck Shape:', style_bottleneck.shape)
    print('Stylizing image. It should not take more than three minutes...')

    # Calculate style bottleneck of the content image
    style_bottleneck_content = run_style_predict(preprocess_image(content_image, 256))

    # Blend the style bottleneck of style image and content image
    content_blending_ratio=0
    style_bottleneck_blended = content_blending_ratio * style_bottleneck_content \
                            + (1 - content_blending_ratio) * style_bottleneck

    # Stylize the content image using the style bottleneck
    stylized_image = run_style_transform(style_bottleneck_blended, preprocessed_content_image)

    image = stylized_image

    if len(image.shape) > 3:
        image = np.squeeze(image)
    
    image = (image * 255).astype(np.uint8)
    return base64_uri_from_array(image)