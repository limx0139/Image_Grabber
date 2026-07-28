# import the necessary packages
import numpy as np
import argparse
import glob
import cv2
from scripts.globalParameters import CANNY_SIGMA, GAUSSIAN_BLUR_INDEX, REFLECTIVE_INDEX
def auto_canny(image, sigma=CANNY_SIGMA, blurIndex = GAUSSIAN_BLUR_INDEX):
    """Runs canny edge detection algorithm with a Gaussian blur and automatically chosen upper and lower bounds and.

    Args:
        image (cv2.UMAT): Array containing image data.
        sigma (int, optional): The distance between upper and lower bounds of the canny algorithm. Defaults to 0.33.
        blurIndex (odd int, optional): The degree of Gaussian blur to apply. Defaults to 5.

    Returns:
        cv2.UMAT: Array containing image data with canny algorithm
    """
	# compute the median of the single channel pixel intensities
    v = np.median(image)
    image = cv2.GaussianBlur(image, (blurIndex,blurIndex), 0)
	# apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
	# return the edged image
    return edged

def removeReflection(gray, reflection_index= REFLECTIVE_INDEX):
    """Removes reflections from the gray-scale image based on the reflection index. Uses the reflective index as a threshold to remove all data below it.
    Args:
        image (cv2.UMAT): Input image (grayscale).
        reflection_index (float): The reflective index of the material. 0.9 seems to work the best for the reflective material in the forge.
        blurIndex (odd int, optional): The degree of Gaussian blur to apply. Defaults to 5.

    Returns:
        cv2.UMAT: image with reflections removed.
    """

    max_value = np.max(gray)
    threshold_value = reflection_index * max_value
    # Apply a threshold to create a binary mask of the reflections
    ret,thresh1 = cv2.threshold(gray, threshold_value, max_value, cv2.THRESH_BINARY)
    return thresh1