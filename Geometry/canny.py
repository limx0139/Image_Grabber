# import the necessary packages
import numpy as np
import argparse
import glob
import cv2
def auto_canny(image, sigma=5, blurIndex = 5):
    """
    Generates edges using the Canny edge detection algorithm with automatic thresholding based on the median of the pixel intensities.
    :param image: Input image (grayscale).
    :param sigma: THresholding parameter. Default is 0.33.
    :return: Edged image.
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

def removeReflection(gray, reflection_index):
    """
    Removes reflections from the gray-scale image based on the reflection index.
    """
    max_value = np.max(gray)
    threshold_value = reflection_index * max_value
    # Apply a threshold to create a binary mask of the reflections
    ret,thresh1 = cv2.threshold(gray, threshold_value, max_value, cv2.THRESH_BINARY)
    return thresh1