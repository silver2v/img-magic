# imgmagik AI
A powerful yet simple flask app that uses magic (aka AI) to restore and improve the quality of images. 

![blabla](https://github.com/silver2v/img-magic/blob/main/static/examples/gif2.gif)

Very easy to use and delivers good results with pictures with a wide range of damage types:

- Restore the quality, colors, and definition of old photos
- Fix scratch damages
- Improve pictures that are not that old (e.g.: from the 80s) or new ones with low res
- Clean visual noise

You can check it out live at https://imgmagik.com

## Motivation

Restoring or improving the quality of photos, specially the ones that have some relevance to us, is something that can give a wow effect and cheer ones day.

It's very hard to find a web or mobile image restoration app out in the wild well rounded enough to bring satisfactory results. Simply doing "AI upscalling" won't do it in a lot of cases.

After researchig many different image restoration engines, I decided to do a implementation of [Bringing-Old-Photos-Back-to-Life](https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life) (with some tweaks) since it was the one that consistently delivered astouding results according to my experience.

This web app was created as the final project for Harvard's [CS50x](https://cs50.harvard.edu/x/) course.

# Main technologies used
- Web app: Flask framework
- Restoration engine: PyToch implementation of [Old Photo Restoration via Deep Latent Space Translation (2020)](https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life) 
- Frontend: some JavaScript, besides the other usual suspects (html, css)


# Requirements
Some dependencies/libraries need at least 8-16GB RAM for instalation. [Tricks](https://linuxize.com/post/how-to-add-swap-space-on-ubuntu-20-04/) can be done to install them with less RAM but the image processing probably will be slow or outright break.

Necessary at least 10GB of free storage space for libraries and pre-trained models.

Python>=3.6 is required to run the code.

The code was tested on MacOS and Ubuntu.

For optimum performance: Nvidia GPU with CUDA installed.



# Instalation
Clone the forked Bringing-Old-Photos-Back-to-Life repository

````
git clone https://github.com/silver2v/Bringing-Old-Photos-Back-to-Life
cd Bringing-Old-Photos-Back-to-Life
````
Clone the Synchronized-BatchNorm-PyTorch repository for

````
cd Face_Enhancement/models/networks/
git clone https://github.com/vacancy/Synchronized-BatchNorm-PyTorch
cp -rf Synchronized-BatchNorm-PyTorch/sync_batchnorm .
cd ../../../
````
````
cd Global/detection_models
git clone https://github.com/vacancy/Synchronized-BatchNorm-PyTorch
cp -rf Synchronized-BatchNorm-PyTorch/sync_batchnorm .
cd ../../
````

Download the landmark detection pretrained model

```
cd Face_Detection/
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
cd ../
````

Download the pretrained model from Azure Blob Storage, put the file `Face_Enhancement/checkpoints.zip` under ./Face_Enhancement, and put the file Global/checkpoints.zip under ./Global. Then unzip them respectively.

```
cd Face_Enhancement/
wget https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life/releases/download/v1.0/face_checkpoints.zip
unzip face_checkpoints.zip
cd ../
cd Global/
wget https://github.com/microsoft/Bringing-Old-Photos-Back-to-Life/releases/download/v1.0/global_checkpoints.zip
unzip global_checkpoints.zip
cd ../../
```
Install dependencies:

```
pip install -r requirements.txt
```


# Usage

Using it locally:
````
flask run
`````

Then acess it via browser and enjoy a simple and intuitive user interface. 

Can be used locally with a flask server or accessed in the cloud with Gunicorn and Nginx running, for example. 

Important: code is set for normal CPU usage (slower):

````
command1 = f"python3 Bringing-Old-Photos-Back-to-Life/run.py --input_folder {complete_upload_folder} \
            --output_folder {complete_upload_folder}/output \
            --GPU -1"
        
command2 = f"python3 Bringing-Old-Photos-Back-to-Life/run.py --input_folder {complete_upload_folder} \
            --output_folder {complete_upload_folder}/output \
            --GPU -1 \
            --with_scratch"
````


To use Nvidia GPU and CUDA (if avaiable), change `GPU` argument to `0` (instead of `-1`) in *both* `command1` and `command2`



# Implementation details and highlights

## Keeeping the original file name
To keep the original name of the uploaded image, the app creates a unique folder with a unique name for each file uploaded. 

```
def folder_name_generator(prefix, size=6, chars=ascii_letters + digits):
    return prefix + '_' + ''.join(choice(chars) for _ in range(size))
````
Where `prefix` is the original name of the image, followed by "_" and 6 pseudo-random charachters. 

With this implementation, the restored image can preserve its original name, instead of the app outputing a file with a name like Dwsk$kaj299@##1io09!Sjsj3939b.jpg

## Image dimension limit and resizing
Images that have too large dimensions can make the processing time unecessarily long or even break it.

To avoid this problem, the code has an option to cap the limit of the dimensions of the image being restored (default cap: 1_000_000 pixels).

If the dimensions of the image exceed the limit, the app will automatically decrease it in loops of -5% until the new dimensions are whithin the limit:

```
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
```

## Safe image name
According to the Flask documentation:
> [T]here is that principle called “never trust user input”. This is also true for the filename of an uploaded file. All submitted form data can be forged, and filenames can be dangerous. For the moment just remember: always use that function to secure a filename before storing it directly on the filesystem.

Because of that, this app uses a funcion from werkzeug.utils called `secure_filename`:
```
from werkzeug.utils import secure_filename
[...]
filename = secure_filename(file.filename)
```

## Image types accepted
```
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
````
File extensions are checked both at the front and backend of the application. 

If the user tries to upload a file with any of those extensions withouth it being a truly image file, the backend check will also reject it:

```
img = imread(file.filename)

        if img is None:
                flash("""Seems like you uploaded a corrupted or not a true image file. 
                    Please try again with a new file.""")
                return redirect(request.url)
```

# Cloud implementation
The code was tested in the cloud using Gunicorn and Nginx.

Depending on the size of the image and/or the processing power of the instance being used, the restoration may take too long and result in `timeout` errors both in Gunicorn and Nginx. To avoid this in:

a) Gunicorn
```
$ TIMEOUT=30000
$ gunicorn app:app --timeout $TIMEOUT 
```
b) Nginx
``` 
$ sudo vi /etc/nginx/nginx.conf
```
and add these proxies:
```
http{
   ...
   proxy_read_timeout 30000;
   proxy_connect_timeout 30000;
   proxy_send_timeout 30000;
   ...
}
```
The 30000 number represents an arbitrary quantity of seconds, which presumably will be enough for all the processing time of the image restoration. 

# Credits
💪 Special thanks to:
- Professor David J. Malan, Brian, Doug, and all CS50's staff
- Ziyu Wan and the other authors of the paper used in the creation of this app
- YT teachers (looking at you, epic Indian dudes)

# License


