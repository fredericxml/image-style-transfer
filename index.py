# import io
# import base64

# import requests
# from PIL import Image
from flask import Flask, render_template, request
from modules.cartoonize import make_cartoon
from modules.pencil_sketch import make_sketch, reset_current_state


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', data={
        'title': 'Home'
    })


@app.route('/sketch-result', methods=['GET', 'POST'])
def process_to_sketch():
    if request.method == 'POST':
        file = request.files['photo'].read()
        
        reset_current_state()
        image_string = make_sketch(file)

        return render_template('result.html', data={
            'title': 'Sketch Result',
            'type': 'sketch',
            'image_src': f"data:image/png;base64,{image_string}"
        })


@app.route('/remake-sketch', methods=['POST'])
def adjust_sketch_sharpness():
    sharpen_value = int(request.get_json()['sharpen_value'])
    
    if sharpen_value < 5:
        sharpen_value = None
    
    image_string = make_sketch(None, sharpen_value)

    return { 'image_src': f"data:image/png;base64,{image_string}" }


@app.route('/cartoon-result', methods=['GET', 'POST'])
def process_to_cartoon():
    if request.method == 'POST':
        file = request.files['photo'].read()

        image_string = make_cartoon(file)

        return render_template('result.html', data={
            'title': 'Cartoon Result',
            'type': 'cartoon',
            'image_src': f"data:image/png;base64,{image_string}"
        })


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
#     img.save(buffered, format="PNG")
#     pngImageB64String = "data:image/png;base64,"
#     pngImageB64String += base64.b64encode(buffered.getvalue()).decode('utf8')


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=True, host='192.168.100.154')