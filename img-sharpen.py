import cv2 as cv
import numpy as np

def unsharp_mask(image, kernel_size=(5, 5), sigma=5.0, amount=5.0, threshold=5):
    """Return a sharpened version of the image, using an unsharp mask."""
    blurred = cv.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened
    
image = cv.imread('static/tyson-1.jpg')
sharpened_image = unsharp_mask(image)
cv.imwrite('tyson8-sharpened.jpg', sharpened_image)

