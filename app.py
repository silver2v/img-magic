from distutils.command.upload import upload
import os
from string import ascii_uppercase
from subprocess import call
from turtle import width
# from types import NoneType
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from random import choice
from string import ascii_letters, digits
from cv2 import imread, IMREAD_UNCHANGED, resize, INTER_AREA, imwrite, imshow, waitKey, destroyAllWindows

ROOT_UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'output/final_output'
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif', 'webp'}

# original = ""
# result = ""

# Configure application
app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER --> nesse momento é desnecessário
# app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER --> nesse momento é desnecessário
app.config['SECRET_KEY'] = 'some random string'
# app.config['MAX_CONTENT_LENGTH'] = 0.01 * 1024 * 1024

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

        
        
        # if (file[-3:] or file[-4:]) not in ALLOWED_EXTENSIONS:
        # if not file in ALLOWED_EXTENSIONS:
        #     flash('Allowed file types only: %s' % (ALLOWED_EXTENSIONS))
        #     return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # print(file and allowed_file(file.filename)

        if not (file and allowed_file(file.filename)):
            flash("Allowed file types: " + ", ".join(str(x) for x in ALLOWED_EXTENSIONS) +  "." + " Please try again.")
            
            #  %s" % (str(x) for x in ALLOWED_EXTENSIONS))
        else:
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
              --GPU -1"
            
            command2 = f"python3 Bringing-Old-Photos-Back-to-Life/run.py --input_folder {complete_upload_folder} \
              --output_folder {complete_upload_folder}/output \
              --GPU -1 \
              --with_scratch"
            

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            #### CREATED THIS STUFF TO DECREASE DIMENTIONS IF ABOVE 1M PIXELS TO SPEED UP PROCESSING
            img = imread(f'{complete_upload_folder}/{filename}')

            if img is None:
                flash("""Seems like you uploaded a corrupted or not a true image file. 
                    Please try again with a new file.""")
                return redirect(request.url)
                # return redirect('/oops')
           
            print("height: " + str(img.shape[0]))
            print("width: ", img.shape[1])

            width = img.shape[1]
            height = img.shape[0]
            pixels = width * height
            print('total pixels:', pixels)

            if pixels > 1_000_000:
                while pixels > 1_000_000:
                    width = int(width * 95 / 100)
                    height = int(height * 95 / 100)
                    dim = (width, height)
                    pixels = width * height
                    print('new total pixels:', pixels)

                #resize image
                resized = resize(img, dim, interpolation = INTER_AREA)

                imwrite(f'{complete_upload_folder}/{filename}', resized)
    
                print('Resized Dimensions : ',resized.shape)


            #### FINISHED THAT PART

            

            # Just for AWS
            extra = request.form.get("extra")
            # extra = ""
            # if extra == "extra":
            #     flash('The option "with scratch" is not available at the moment, please try again with it unchecked.')
            #     return redirect(request.url)

            if not extra == "extra":
                call(command1, shell=True)
            else: 
                call(command2, shell=True)

            
            ## getting the links to post the pre and post pics
            original = complete_upload_folder + "/" + filename

            #sometimes the program changes the extension of the
            #output file to png (eg if the original file was a jpg), 
            # so that must be taken into consideration
            
            output_filename = None
            for file in os.listdir(output_folder):
                output_filename = file

            ## if for some reason execution didn't finish (must change text)
            if not output_filename:
                return redirect('/oops')
            
            result = output_folder + "/" + output_filename

            

            #return render_template("test.html", folder=complete_upload_folder, filename=filename)
            # return render_template("test3.html", result=result)
            
            #return """<img src=f"{output_folder}/{filename}">"""

            # return redirect(url_for('download_file', name=filename))
           
            return render_template('result.html', original=original, result=result )
            # return redirect(url_for('voila'))

    return render_template('index2.html')

# not being used atm
@app.route('/test')
def show_test():
    return render_template('test.html')


# @app.route('/<name>')
# def download_file(name):
#     return send_from_directory(app.config[OUTPUT_FOLDER], name)



@app.route('/oops')
def oops():
    return render_template("error.html")

@app.route('/about')
def about():
    return render_template("about.html")
    
    
    

if __name__=="__main__":
    app.run(host='0.0.0.0')
