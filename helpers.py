from string import ascii_letters, digits
from random import choice

# Functions that checks if extension of the file is allowed
#   the function returns a boolean value
def extension_check(image_name, allowed_extensions):
    return '.' in image_name and \
        image_name.rsplit('.', 1)[1].lower() in allowed_extensions


# Function used later to help creating the 2nd part of the  name of the folder where both 
#   original image (input) and its restored version (output)
#   will be stored (1st part of the name of the folder, aka prefix is file name itself)
#   This makes each folder name unique, and name of image can be preserved)
#   Ex. folder name: my-image_kjdjksi.jpg
def folder_name_generator(prefix, size=6, chars=ascii_letters + digits):
    return prefix + '_' + ''.join(choice(chars) for _ in range(size))

