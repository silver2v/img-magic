import os
from subprocess import call
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from cv2 import imread, resize, INTER_AREA, imwrite, imshow, waitKey, destroyAllWindows
from helpers import extension_check, folder_name_generator


ROOT_UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'output/final_output'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
GPU = False

PIXEL_LIMIT = True
# if the picture has bigger pixel dimensions, the app will automatically downsize it in 5% increments
PIXEL_LIMIT_VALUE = 1_000_000

# Initializing flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'some random string'


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
   
        if not (file and extension_check(file.filename, ALLOWED_EXTENSIONS)):
            flash("Allowed file types: " + ", ".join(str(x) for x in ALLOWED_EXTENSIONS) +  "." + " Please try again.")

        print('hey')
        filename = secure_filename(file.filename)

        new_folder = folder_name_generator(filename)
        complete_upload_folder = f'{ROOT_UPLOAD_FOLDER}/{new_folder}'
        
        os.makedirs(complete_upload_folder)

        output_folder = f'{complete_upload_folder}/output/final_output'
        #Obs.: not necessary to makedir output_folder because "run.py" will do it by itself


        # The CLI commands the original implementation uses

        if GPU == True:
            gpu_value = "0"
        else:
            gpu_value = "-1"

        command1 = f"python3 Bringing-Old-Photos-Back-to-Life/run.py --input_folder {complete_upload_folder} \
            --output_folder {complete_upload_folder}/output \
            --GPU {gpu_value}"
        
        command2 = f"python3 Bringing-Old-Photos-Back-to-Life/run.py --input_folder {complete_upload_folder} \
            --output_folder {complete_upload_folder}/output \
            --GPU {gpu_value} \
            --with_scratch"
        
        file.save(os.path.join(complete_upload_folder, filename))

        img = imread(f'{complete_upload_folder}/{filename}')

        if img is None:
            flash("""Seems like you uploaded a corrupted or not a true image file. 
                Please try again with a new file.""")
            return redirect(request.url)
        
        # Checking the image dimensions in pixels         
        print("height: " + str(img.shape[0]))
        print("width: ", img.shape[1])

        height = img.shape[0]
        width = img.shape[1]
        
        pixels = width * height
        print('total pixels:', pixels)

        
        # If dimenions of image bigger than  max_pixels, reduce 5% (while loop)
        if PIXEL_LIMIT == True and pixels > PIXEL_LIMIT_VALUE:
            while pixels > PIXEL_LIMIT_VALUE:
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


