from distutils.command.upload import upload
import os
from string import ascii_uppercase
from subprocess import call
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from random import choice
from string import ascii_letters, digits


UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output/final_output'
# UPLOAD_FOLDER = '/Users/rudi/Projects/Photo_app/uploads'
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif'}

# Configure application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['SECRET_KEY'] = 'some random string'


command = "python3 Bringing-Old-Photos-Back-to-Life/run.py"

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def id_generator(prefix='img', size=6, chars=ascii_letters + digits):
    return prefix + '_' + ''.join(choice(chars) for _ in range(size))


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        print(file.filename)
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # print(file and allowed_file(file.filename)

        if allowed_file(file.filename):
            print('hey')
            filename = secure_filename(file.filename)

            new_folder = id_generator(filename)
            upload_folder = f'uploads/{new_folder}'

            while os.path.exists(upload_folder):
                new_folder = id_generator(filename)
                upload_folder = f'uploads/{new_folder}'
            
            os.makedirs(upload_folder)
            
            app.config['UPLOAD_FOLDER'] = upload_folder
            output_folder = f'{upload_folder}/output/final_output'
            app.config['OUTPUT_FOLDER'] = output_folder

            command1 = f"python3 Bringing-Old-Photos-Back-to-Life/run.py --input_folder {upload_folder} \
              --output_folder {upload_folder}/output \
              --GPU -1"

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            call("rm uploads/.DS_Store", shell=True)
            call(command1, shell=True)

            return redirect(url_for('download_file', name=filename))

    return render_template('index.html')


@app.route('/output/<name>')
def download_file(name):
    return send_from_directory(app.config["OUTPUT_FOLDER"], name)

