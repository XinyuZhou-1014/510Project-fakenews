import os
import time
from flask import render_template
from flask import Flask
from flask import request
from werkzeug.utils import secure_filename

file_save_path = "../temp/test_input.txt"
upload_flag_file_path = "../temp/model_start.tmp"
output_file_path = "../temp/test_output.txt"
finish_flag_file_path = "../temp/model_finish.tmp"

app = Flask(__name__)


@app.route('/')
def default():
    return render_template('main.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    print("here!")
    if request.method == 'POST':
        print(request.files)
        f = request.files['fileToUpload']
        f.save(file_save_path)
        with open(upload_flag_file_path, 'w') as fw:
            pass
        output = read_output()
        return render_template('main.html', status="File uploaded", output=output)
    return render_template('main.html', status="Not Post?")


def read_output():
    # return "hahaha"
    while not (os.path.exists(output_file_path) and os.path.exists(finish_flag_file_path)):
        time.sleep(0.2)
    os.remove(finish_flag_file_path)
    return ''.join(open(output_file_path).readlines())

