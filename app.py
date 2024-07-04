import utilities.texts as texts
from secret.env import *
from flask import Flask, render_template, request
from modules.cartoonize import make_cartoon
from modules.pencil_sketch import make_sketch
from modules.style_transfer import do_style_transfer
from utilities.utils import print_current_memory_usage, save_image, update_google_sheet, write_on_google_sheet


app = Flask(__name__)
print_current_memory_usage('App start')


@app.route('/', methods=['GET'])
def home():
    feature_list = texts.feature_list()
    banner_description = texts.banner_description()
    style_template_list = texts.style_template_list()

    print_current_memory_usage()

    return render_template('home.html',
        page_title='Home',
        features=feature_list,
        banner_description=banner_description,
        style_templates=style_template_list
    )


@app.route('/download', methods=['GET', 'POST'])
def update_download_status():
    if request.method == 'POST':
        range_name = request.get_json().get('range_name')

        # Take only sheet name with the last cell
        range_name = range_name.split('!')
        range_name[-1] = range_name[-1].split(':')[-1]
        range_name = '!'.join(range_name)

        return update_google_sheet(range_name, [1])
    else:
        return {'message': 'Thanks for downloading'}


@app.route('/style-blender', methods=['GET', 'POST'])
def process_style_transfer():
    if request.method == 'POST':
        content_image  = request.files['image_0'].read()
        style_filename = request.form.get('style_filename')

        content_image_id, content_image_link = save_image(content_image)

        # Not using the template style image
        if style_filename is None:
            style_image = request.files['image_1'].read()
            style_image_id, style_image_link = save_image(style_image)

            style_filename = request.files['image_1'].filename
            style_filesize = round(len(style_image) / 1e6, 3) # Filesize in megabytes

            from_style_template = False
        else:
            style_image = style_filename
            from_style_template = True

            style_image_id = f'template:{style_filename}'
            style_image_link = ''
            style_filename = ''
            style_filesize = ''
        
        result = do_style_transfer(content_image, style_image, from_style_template)

        updated_range = write_on_google_sheet('Style Transfer', {
            # Content image
            'content_image_id': content_image_id,
            'content_image_link': content_image_link,
            'content_filename': request.files['image_0'].filename,
            'content_dimension': result['content_dimension'],
            'content_filesize': round(len(content_image) / 1e6, 3), # Filesize in megabytes
            # Style image
            'style_image_id': style_image_id,
            'style_image_link': style_image_link,
            'style_filename': style_filename,
            'style_dimension': result['style_dimension'] if not from_style_template else '',
            'style_filesize': style_filesize
        })

        print_current_memory_usage('Style Transfer')
        return {'result': result['image'], 'range_name': updated_range}
    else:
        return {'message': 'Style blender is here! Could you please inform me if you require API access?'}


@app.route('/cartoonize', methods=['GET', 'POST'])
def process_to_cartoon():
    if request.method == 'POST':
        image = request.files['image_0'].read()
        result = make_cartoon(image)

        image_id, image_link = save_image(image)
        updated_range = write_on_google_sheet('Cartoonize', {
            'image_id': image_id,
            'image_link': image_link,
            'filename': request.files['image_0'].filename,
            'dimension': result['dimension'],
            'filesize': round(len(image) / 1e6, 3) # Filesize in megabytes
        })

        print_current_memory_usage('Cartoonize')
        return {'result': result['image'], 'range_name': updated_range}
    else:
        return {'message': 'Cartoonizer is here! Could you please inform me if you require API access?'}


@app.route('/pencil-sketch', methods=['GET', 'POST'])
def process_to_sketch():
    if request.method == 'POST':
        image = request.files['image_0'].read()
        sharpen_factor = request.form.get('sharpen_factor')
        range_name = request.form.get('range_name')

        # Adjust sketch sharpness on uploaded image
        # New image doesn't have sharpen_factor value
        # Set sharpen_factor to None if it's too small
        if sharpen_factor is not None:
            sharpen_factor = int(sharpen_factor)
            if sharpen_factor < 5:
                sharpen_factor = None
        
        result = make_sketch(image, sharpen_factor)

        # New image also doesn't have range_name yet
        if range_name is None:
            image_id, image_link = save_image(image)
            updated_range = write_on_google_sheet('Pencil Sketch', {
                'image_id': image_id,
                'image_link': image_link,
                'filename': request.files['image_0'].filename,
                'dimension': result['dimension'],
                'filesize': round(len(image) / 1e6, 3), # Filesize in megabytes
                'sharpen_factor': -1
            })
            range_name = updated_range
        
        # Adjust sketch sharpness
        # Only do update on production environment
        elif os.getenv('MODE') == 'production':
            # Take only sheet name with the sharpen_factor cell
            # Column H is sharpen_factor
            range_name = range_name.split('!')
            range_name[1] = 'H' + range_name[1].split(':')[-1][1:]
            range_name = '!'.join(range_name)
            
            if sharpen_factor is None:
                sharpen_factor = -1

            update_google_sheet(range_name, [sharpen_factor])

        print_current_memory_usage('Pencil Sketch')
        return {'result': result['image'], 'range_name': range_name}
    else:
        return {'message': 'Pencil artist is here! Could you please inform me if you require API access?'}


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, host='192.168.100.103', port=5000)