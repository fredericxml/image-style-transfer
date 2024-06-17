import cv2
import numpy as np
import tensorflow as tf
from utilities import base_path, base64_string_from_buffer


# https://www.kaggle.com/models/google/arbitrary-image-stylization-v1/
model_path_predict = base_path('models', 'Style Transfer', 'v1-predict_fp16.tflite')
model_path_transfer = base_path('models', 'Style Transfer', 'v1-transfer_fp16.tflite')

interpreter_predict = tf.lite.Interpreter(model_path=model_path_predict)
interpreter_transfer = tf.lite.Interpreter(model_path=model_path_transfer)
interpreter_predict.allocate_tensors()
interpreter_transfer.allocate_tensors()

content_image_path=base_path('models', 'header-1.png')
style_image_path=base_path('models', "640px-'The_Visitor',_120x100cm,_Oil_on_Belgian_linen_by_Hennie_Niemann_jnr_signed_and_dated_lower_left,_2019.jpg")
style_image_path=base_path('static','images', "header-1.png")


def load_image(image_buffer, target_size, from_buffer=True):
    if from_buffer:
        image = cv2.imdecode(np.frombuffer(image_buffer, np.uint8), cv2.IMREAD_COLOR)
    else:
        image = cv2.imread(image_buffer)

    image = cv2.resize(image, (target_size, target_size))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.array(image).astype(np.float32) / 255.0
    image = np.expand_dims(image, axis=0)
    return image


def postprocess_image(image):
    image = np.squeeze(image)
    image = (image * 255).astype(np.uint8)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def do_style_transfer(content_image_file):
    content_image = load_image(content_image_file, target_size=384)
    style_image = load_image(style_image_path, target_size=256, from_buffer=False)
    
    interpreter_predict.set_tensor(interpreter_predict.get_input_details()[0]['index'], style_image)
    interpreter_predict.invoke()
    style_bottleneck = interpreter_predict.get_tensor(interpreter_predict.get_output_details()[0]['index'])
    
    interpreter_transfer.set_tensor(interpreter_transfer.get_input_details()[0]['index'], content_image)
    interpreter_transfer.set_tensor(interpreter_transfer.get_input_details()[1]['index'], style_bottleneck)
    interpreter_transfer.invoke()
    raw_output = interpreter_transfer.get_tensor(interpreter_transfer.get_output_details()[0]['index'])

    final_output = postprocess_image(raw_output)
    
    return base64_string_from_buffer(final_output)