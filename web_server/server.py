
from flask import render_template
from flask import Flask
app = Flask(__name__)

@app.route('/')
def default():
    return render_template('main.html')

from flask import request
from werkzeug.utils import secure_filename

file_save_path = "../510project-fakenews/test_input.txt"

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    print("here!")
    if request.method == 'POST':
        print(request.files)
        f = request.files['fileToUpload']
        f.save(file_save_path)
        output = read_output()
        return render_template('main.html', status="File uploaded", output=output)
    return render_template('main.html', status="Not Post?")

output_file_path = "../510project-fakenews/test_output.txt"
flag_file_path = "../510project-fakenews/model_finish.tmp"

import os
import time

def read_output():
    # return "hahaha"
    while not (os.path.exists(output_file_path) and os.path.exists(flag_file_path)):
        time.sleep(0.2)
    os.remove(flag_file_path)
    return ''.join(open(output_file_path).readlines())

