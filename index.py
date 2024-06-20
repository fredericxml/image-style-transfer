import texts
from flask import Flask, render_template, request
from modules.cartoonize import make_cartoon
from modules.pencil_sketch import make_sketch
from modules.style_transfer import do_style_transfer


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    feature_list = texts.feature_list()
    banner_description = texts.banner_description()
    style_template_list = texts.style_template_list()

    return render_template('home.html',
        page_title='Home',
        features=feature_list,
        banner_description=banner_description,
        style_templates=style_template_list
    )


@app.route('/style-blender', methods=['GET', 'POST'])
def process_style_transfer():
    if request.method == 'POST':
        content_image  = request.files['image_0'].read()

        style_filename = request.form.get('style_filename')
        if style_filename is None:
            style_image = request.files['image_1'].read()
            from_style_template = False
        else:
            style_image = style_filename
            from_style_template = True
        
        result = do_style_transfer(content_image, style_image, from_style_template)
        return {'result': result}
    else:
        return {'message': 'Style blender is here! Could you please inform me if you require API access?'}


@app.route('/cartoonize', methods=['GET', 'POST'])
def process_to_cartoon():
    if request.method == 'POST':
        image = request.files['image_0'].read()
        result = make_cartoon(image)
        return {'result': result}
    else:
        return {'message': 'Cartoonizer is here! Could you please inform me if you require API access?'}


@app.route('/pencil-sketch', methods=['GET', 'POST'])
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
        return {'result': result}
    else:
        return {'message': 'Pencil artist is here! Could you please inform me if you require API access?'}


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, host='192.168.100.103', port=5000)