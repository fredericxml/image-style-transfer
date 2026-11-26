from flask import Flask, render_template, request
from werkzeug.exceptions import BadRequest, HTTPException, RequestEntityTooLarge

from config import HOST, PORT, MAX_IMAGE_BYTES, MAX_REQUEST_BYTES
from modules.cartoonize import make_cartoon
from modules.pencil_sketch import make_sketch
from modules.style_transfer import do_style_transfer
from utilities import analytics, texts
from utilities.image_validation import InvalidImage
from utilities.utils import print_current_memory_usage

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_REQUEST_BYTES


def read_upload(field):
    upload = request.files.get(field)
    if upload is None:
        raise InvalidImage(f'Missing required image: {field}.')
    data = upload.stream.read(MAX_IMAGE_BYTES + 1)
    if not data:
        raise InvalidImage('Image is empty.')
    if len(data) > MAX_IMAGE_BYTES:
        raise RequestEntityTooLarge()
    return data


def parse_sharpness(value):
    if value is None:
        return None
    try:
        factor = int(value)
    except (ValueError, TypeError) as exc:
        raise InvalidImage('Sharpness must be an integer from 4 to 40.') from exc
    if not 4 <= factor <= 40:
        raise InvalidImage('Sharpness must be an integer from 4 to 40.')
    return None if factor == 4 else factor


def process_image(operation, description):
    try:
        result = operation()
        print_current_memory_usage(description)
        return {'result': result['image'], 'range_name': result.get('range_name')}
    except InvalidImage as exc:
        return {'error': str(exc)}, 400
    except HTTPException:
        raise
    except Exception:
        app.logger.exception('Image processing failed: %s', description)
        return {'error': 'Image processing failed. Please try again.'}, 500


@app.errorhandler(BadRequest)
def bad_request(error):
    return {'error': 'Malformed request.'}, 400


@app.errorhandler(RequestEntityTooLarge)
def upload_too_large(error):
    return {'error': 'Each image must be at most 10 MiB; request limit is 21 MiB.'}, 413


@app.get('/')
def home():
    return render_template('home.html', page_title='Home',
                           features=texts.feature_list(),
                           banner_description=texts.banner_description(),
                           style_templates=texts.style_template_list(),
                           analytics_enabled=analytics.enabled())


def attach_tracking(sheet, result, image, **kwargs):
    if request.form.get('analytics_consent') == 'true':
        result['range_name'] = analytics.record_processing(
            sheet, image, request.files['image_0'].filename, result, **kwargs)
    return result


@app.route('/style-blender', methods=['GET', 'POST'])
def process_style_transfer():
    if request.method == 'GET':
        return {'message': 'Neural style transfer is available via POST.'}

    def operation():
        content = read_upload('image_0')
        template = request.form.get('style_filename')
        if template is not None:
            if 'image_1' in request.files:
                raise InvalidImage('Choose a style template or upload a style image, not both.')
            result = do_style_transfer(content, template, True)
            return attach_tracking('Style Transfer', result, content, template=template)
        style = read_upload('image_1')
        result = do_style_transfer(content, style, False)
        return attach_tracking('Style Transfer', result, content, style=style,
                               style_filename=request.files['image_1'].filename)
    return process_image(operation, 'Style Transfer')


@app.route('/cartoonize', methods=['GET', 'POST'])
def process_to_cartoon():
    if request.method == 'GET':
        return {'message': 'Cartoonization is available via POST.'}

    def operation():
        image = read_upload('image_0')
        return attach_tracking('Cartoonize', make_cartoon(image), image)
    return process_image(operation, 'Cartoonize')


@app.route('/pencil-sketch', methods=['GET', 'POST'])
def process_to_sketch():
    if request.method == 'GET':
        return {'message': 'Pencil sketch generation is available via POST.'}

    def operation():
        image = read_upload('image_0')
        factor = parse_sharpness(request.form.get('sharpen_factor'))
        result = make_sketch(image, factor)
        return attach_tracking('Pencil Sketch', result, image, factor=factor,
                               previous=request.form.get('range_name'))
    return process_image(operation, 'Pencil Sketch')


@app.route('/download', methods=['GET', 'POST'])
def update_download_status():
    if request.method == 'GET':
        return {'message': 'Download tracking is available via POST.'}
    data = request.get_json(silent=True)
    token = data.get('range_name') if isinstance(data, dict) else None
    return {'tracked': analytics.record_download(token)}


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=False)
