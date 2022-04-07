from distutils.command.upload import upload
import os
from string import ascii_uppercase
from subprocess import call
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from random import choice
from string import ascii_letters, digits
import webbrowser


ROOT_UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'output/final_output'
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif'}

# Configure application
app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER --> nesse momento é desnecessário
# app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER --> nesse momento é desnecessário
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
            complete_upload_folder = f'{ROOT_UPLOAD_FOLDER}/{new_folder}'

            # (tinha isso, n lembro porque coloquei, parece desnecessário)
            # while os.path.exists(upload_folder):
            #     new_folder = id_generator(filename)
            #     upload_folder = f'uploads/{new_folder}'
            
            os.makedirs(complete_upload_folder)
            
            app.config['UPLOAD_FOLDER'] = complete_upload_folder
            output_folder = f'{complete_upload_folder}/output/final_output'
            app.config['OUTPUT_FOLDER'] = output_folder

            command1 = f"python3 Bringing-Old-Photos-Back-to-Life/run.py --input_folder {complete_upload_folder} \
              --output_folder {complete_upload_folder}/output \
              --GPU -1" ##\
              ##--with_scratch"

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            call(command1, shell=True)
            
            #return render_template("test.html", folder=complete_upload_folder, filename=filename)
            
            #return """<img src=f"{output_folder}/{filename}">"""

            return redirect(url_for('download_file', name=filename))

            # return render_template('test.html', output_folder=output_folder, filename=filename )

    return render_template('index.html')

# not being used atm
@app.route('/test')
def show_test():
    return render_template('test.html')


@app.route('/<name>')
def download_file(name):
    return send_from_directory(app.config["OUTPUT_FOLDER"], name)
    
    

if __name__=="__main__":
    app.run(host='0.0.0.0', port=8080)
