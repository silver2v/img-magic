import os
from subprocess import call
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from random import choice
from string import ascii_letters, digits
from cv2 import imread, resize, INTER_AREA, imwrite, imshow, waitKey, destroyAllWindows


ROOT_UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'output/final_output'


# Initializing flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'some random string'

# Functions that checks if extension of the file is allowed
#   the function returns a boolean value
def allowed_extension(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function used later to help creating the 2nd part of the  name of the folder where both 
#   original image (input) and its restored version (output)
#   will be stored (1st part of the name of the folder, aka prefix is file name itself)
#   This makes each folder name unique, and name of image can be preserved)
#   Ex. folder name: my-image_kjdjksi.jpg
def folder_name_generator(prefix, size=6, chars=ascii_letters + digits):
    return prefix + '_' + ''.join(choice(chars) for _ in range(size))


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if not request.method == 'POST':
     return render_template('index.html')
    
    else:
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        # If the user does not select a file, the browser submits an
        #   empty file without a filename.
        if file.filename == '':
            flash('No selected file. Please choose an image and try again.')
            return redirect(request.url)
   
        if not (file and allowed_extension(file.filename)):
            flash("Allowed file types: " + ", ".join(str(x) for x in ALLOWED_EXTENSIONS) +  "." + " Please try again.")

        img = imread(file.filename)

        if img is None:
                flash("""Seems like you uploaded a corrupted or not a true image file. 
                    Please try again with a new file.""")
                return redirect(request.url)
            
        else:
            print('hey')
            filename = secure_filename(file.filename)

            new_folder = folder_name_generator(filename)
            complete_upload_folder = f'{ROOT_UPLOAD_FOLDER}/{new_folder}'
            
            os.makedirs(complete_upload_folder)


            output_folder = f'{complete_upload_folder}/output/final_output'
            #Obs.: not necessary to makedir output_folder because "run.py" will do it by itself
        
            # The CLI commands the original implementation uses
            command1 = f"python3 Bringing-Old-Photos-Back-to-Life/run.py --input_folder {complete_upload_folder} \
              --output_folder {complete_upload_folder}/output \
              --GPU -1"
            
            command2 = f"python3 Bringing-Old-Photos-Back-to-Life/run.py --input_folder {complete_upload_folder} \
              --output_folder {complete_upload_folder}/output \
              --GPU -1 \
              --with_scratch"
            

            file.save(os.path.join(complete_upload_folder, filename))
           
            # Checking the image dimensions in pixels         
            print("height: " + str(img.shape[0]))
            print("width: ", img.shape[1])

            height = img.shape[0]
            width = img.shape[1]
            
            pixels = width * height
            print('total pixels:', pixels)

            reduce = True
            max_pixels = 1_000_000
            
            # If dimenions of image bigger than  max_pixels, reduce 5% (while loop)
            if reduce == True and pixels > max_pixels:
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

            #### FINISHED THE ABOVE PART

            # Checking if option "with scratch" is marked (here name as "extra")
            extra = request.form.get("extra")
    
            if not extra == "extra":
                call(command1, shell=True)
            else: 
                call(command2, shell=True)

            
            ## getting the links to post the pre and post pics
            original = complete_upload_folder + "/" + filename

            #sometimes "restoration engine" (original implementation program) changes the extension of the
            #output file to png (eg sometimes if the original file was a jpg), 
            # so that must be taken into consideration
            
            output_filename = None
            for file in os.listdir(output_folder):
                output_filename = file

            ## if for some reason execution didn't finish (must change text)
            if not output_filename:
                return redirect('/oops')
            
            result = output_folder + "/" + output_filename
           
            return render_template('result.html', original=original, result=result )
          

@app.route('/oops')
def oops():
    return render_template("error.html")

@app.route('/about')
def about():
    return render_template("about.html")
    
    
if __name__=="__main__":
    app.run(host='0.0.0.0')


### Bellow are parts of code from previous versions that are not being used anymore

# app.config['UPLOAD_FOLDER'] = complete_upload_folder
# app.config['OUTPUT_FOLDER'] = output_folder

# @app.route('/<name>')
# def download_file(name):
#     return send_from_directory(app.config[OUTPUT_FOLDER], name)