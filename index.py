import random

# import requests
# from PIL import Image
from flask import Flask, render_template, request
from modules.cartoonize import make_cartoon
from modules.pencil_sketch import make_sketch
from modules.style_transfer_inceptionv3 import do_style_transfer


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    banner_description_list = [
        'It merges technology and creativity, transforming photos with diverse artistic styles.',
        'Using Generative AI, ordinary photos are turned into captivating visual masterpieces.',
        'It offers endless possibilities for creative expression and artistic innovation.',
        'Generative AI redefines how we perceive and interact with visual art.',
        'It blends art and technology to inspire awe and imagination.',
        'Artistic styles of famous painters can be seamlessly applied to photos using AI.',
        'It allows for the creation of unique visual aesthetics.',
        'It transforms simple snapshots into captivating visual compositions.',
        'It offers a new way to explore and experiment with artistic styles.',
        'Through Generative AI, photos are transformed into personalized works of art.',
        'It bridges the gap between technology and artistic creativity.',
        'Using Generative AI, photos can emulate the styles of renowned painters effortlessly.',
        'It offers a novel approach to enhancing visual storytelling.',
        'It enhances photos by infusing them with artistic flair.',
        'It unlocks new potentials for digital artistry and creativity.',
        'By leveraging Generative AI, users can transform their photos into visually striking artworks.',
        'It automates the application of artistic styles to photos, enhancing creativity.',
        'Using Generative AI, users can apply diverse artistic inspirations to their photos seamlessly.',
        'It expands the possibilities of digital artistry with automated style application.',
        'It empowers users to create unique visual narratives from their photos using Generative AI.'
    ]
    banner_description = 'Style Dreamer is a tool to transform photos into stunningly styled images. '
    banner_description += random.choice(banner_description_list)

    feature_list = [
        {
            'title': 'Style Blender',
            'description': 'Turn your photos into stunning artworks with our style blender technology.'},
        {
            'title': 'Cartoonize',
            'description': 'Transform your photos into whimsical, animated masterpieces.'},
        {
            'title': 'Pencil Sketch',
            'description': 'Transform your photos into whimsical, animated masterpieces.'},
    ]
    for feature in feature_list:
        feature['id'] = '-'.join(feature['title'].lower().split())

    return render_template('home.html',
        page_title='Home',
        banner_description=banner_description,
        features=feature_list
    )


@app.route('/style-blender', methods=['POST'])
def process_style_transfer():
    if request.method == 'POST':
        content_image  = request.files['image_0'].read()
        style_image = request.files['image_1'].read()
        result = do_style_transfer(content_image, style_image)
        return {
            'result': result
        }


@app.route('/cartoonize', methods=['POST'])
def process_to_cartoon():
    if request.method == 'POST':
        image = request.files['image_0'].read()
        result = make_cartoon(image)
        return {
            'result': result
        }


@app.route('/pencil-sketch', methods=['POST'])
def process_to_sketch():
    if request.method == 'POST':
        image = request.files['image_0'].read()
        sharpen_factor = request.form.get('sharpen_factor')

        # Adjust sketch sharpness
        if sharpen_factor is not None:
            sharpen_factor = int(sharpen_factor)
            if sharpen_factor < 5:
                sharpen_factor = None
        
        result = make_sketch(image, sharpen_factor)
        return {
            'result': result
        }


# @app.route('/remake-sketch', methods=['POST'])
# def adjust_sketch_sharpness():
#     sharpen_value = int(request.get_json()['sharpen_value'])
#     print(sharpen_value)
    
#     if sharpen_value < 5:
#         sharpen_value = None
    
#     image_string = make_sketch(None, sharpen_value)

#     return { 'result': f'data:image/png;base64,{image_string}' }


# def backup(file):
#     response = requests.post('https://freeimage.host/api/1/upload', data={
#         'key': '6d207e02198a847aa98d0a2a901485a5',
#         'action': 'upload',
#         'source': base64.b64encode(file)
#     }).json()

#     url = response['image']['url']
#     response = requests.get(url, stream=True)
#     img = Image.open(response.raw)
#     buffered = io.BytesIO()
#     img.save(buffered, format='PNG')
#     pngImageB64String = 'data:image/png;base64,'
#     pngImageB64String += base64.b64encode(buffered.getvalue()).decode('utf8')


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, host='192.168.100.103',port=5000)