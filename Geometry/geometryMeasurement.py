



import cv2
import numpy as np


def measureVerticalGeometry(edged, ROI_WIDTH):
    '''
    Measure the lengths in each vertical ROI and return the lengths as a np list. The lengths are measured in pixels.
    '''
    num_rows, num_cols = edged.shape[:2]
    results = np.zeros(num_cols // ROI_WIDTH + 1)
    for x in range(0, num_cols, ROI_WIDTH):
        # Extract the vertical ROI from the edged image
        vertical_ROI = edged[:, x:x + ROI_WIDTH]
        max_y = findMaxY(vertical_ROI)
        min_y = findMinY(vertical_ROI)
        length = max_y - min_y if max_y is not None and min_y is not None else 0
        results[x // ROI_WIDTH] = length
    return results

def findMaxY(ROI):
    '''
    Find the maximum y-coordinate of the white pixels in the vertical ROI.
    '''
    # Find the coordinates of the white pixels in the vertical ROI
    white_pixels = np.column_stack(np.where(ROI == 255))
    
    if len(white_pixels) == 0:
        return None  # No white pixels found
    
    # Get the maximum y-coordinate (row index) of the white pixels
    max_y = np.max(white_pixels[:, 0])
    
    return max_y

def findMinY(ROI):
    '''
    Find the minimum y-coordinate of the white pixels in the vertical ROI.
    '''
    # Find the coordinates of the white pixels in the vertical ROI
    white_pixels = np.column_stack(np.where(ROI == 255))
    
    if len(white_pixels) == 0:
        return None  # No white pixels found
    
    # Get the minimum y-coordinate (row index) of the white pixels
    min_y = np.min(white_pixels[:, 0])
    
    return min_y