



import cv2
import numpy as np


def measureVerticalGeometry(verticalGeometry, edged, numVerticalROIs):
    '''
    Measure the lengths in each vertical ROI and return the lengths as a np list. The lengths are measured in pixels.
    '''
    num_rows, num_cols = edged.shape[:2]
    width = num_cols // numVerticalROIs
    coords = []
    for x in range(numVerticalROIs):
        print(f"Measuring vertical geometry for ROI {x+1}...")
        print(verticalGeometry)
        # Extract the vertical ROI from the edged image
        if x == numVerticalROIs - 1:  # Last ROI may be wider due to integer division
            vertical_ROI = edged[:, x * width:num_cols]
        else:
            vertical_ROI = edged[:, x * width:x * width + width]
        max_y = findMaxY(vertical_ROI)
        min_y = findMinY(vertical_ROI)
        x_pos = x * width + width // 2  # Calculate the x position for drawing
        length = max_y - min_y if max_y is not None and min_y is not None else 0
        verticalGeometry[x] = length
        coords.append((min_y, max_y, x_pos))  # Store min_y, max_y, and x position for drawing
    return coords

    

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