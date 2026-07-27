



import cv2
import numpy as np


def measureVerticalGeometry(verticalGeometry, edged, numVerticalROIs):
    '''
    Measure the lengths in each vertical ROI and return the lengths as a np list. The lengths are measured in pixels.
    This function takes in verticalGeometry, an array to be updated with the lengths found in each ROI, edged, the thresholded image nparray, and numVerticalROIs, the number of vertical ROIs.
    Returns an array of tuples, in the form ((x_pos, min_y), (x_pos, max_y), length) for each ROI, that is the coords of min and max points as well as the length.
    '''
    num_rows, num_cols = edged.shape[:2]
    width = num_cols // numVerticalROIs
    coords = []
    for x in range(numVerticalROIs):
        # print(f"Measuring vertical geometry for ROI {x+1}...")
        # print(verticalGeometry)
        # Extract the vertical ROI from the edged image
        if x == numVerticalROIs - 1:  # Last ROI may be wider due to integer division
            vertical_ROI = edged[:, x * width:num_cols]
        else:
            vertical_ROI = edged[:, x * width:x * width + width]

        z = findMinMaxLengthY(vertical_ROI)
        if z is None:
            verticalGeometry[x] = 0
            coords.append(None)
            continue
        (min_y, x1), (max_y, x2), length = z

        x_pos = x * width + width // 2  # Calculate the x position for drawing
        verticalGeometry[x] = length
        coords.append((x_pos, min_y), (x_pos, max_y), length)  # Store min_y, max_y, and x position for drawing

    return coords

def measureHorizontalGeometry(horizontalGeometry, edged, numHorizontalROIs):
    '''
    Measure the lengths in each horizontal ROI and return the lengths as a np list. The lengths are measured in pixels.
    This function takes in horizontalGeometry, an array to be updated, edged, the thresholded image nparray, and numHorizontalROIs, the number of horizontal ROIs.
    Returns an array of tuples, in the form ((min_x, y_pos), (max_x, y_pos), length) for each ROI.
    '''
    num_rows, num_cols = edged.shape[:2]
    height = num_rows // numHorizontalROIs
    coords = []
    for y in range(numHorizontalROIs):

        # Extract the horizontal ROI from the edged image
        if y == numHorizontalROIs - 1:  # Last ROI may be taller due to integer division error
            horizontal_ROI = edged[y * height:num_rows, :]
        else:
            horizontal_ROI = edged[y * height:y * height + height, :]
        z = findMinMaxLengthX(horizontal_ROI)
        if z is None:
            horizontalGeometry[y] = 0
            coords.append(None)
            continue
        (y1, min_x), (y2, max_x), length = z

        y_pos = y * height + height // 2 # Calculate the y position for drawing
        horizontalGeometry[y] = length
        coords.append(((min_x, y_pos), (max_x, y_pos), length))  # Store min_x, max_x, and y position for drawing
    return coords

    


def findMinMaxLengthX(ROI):
    '''
    Given a thresholded nparray ROI, find the points corresponding to minimum x, maximum x and the horizontal length as an 3-tuple.
    '''
    # Find the coordinates of the white pixels in the vertical ROI
    white_pixels = np.column_stack(np.where(ROI == 255))
    
    
    if len(white_pixels) <= 1:
        return None  # No white pixels found
    white_pixels = sorted(white_pixels, key=lambda x: x[1])
    # Get the maximum x-coordinate (column index) of the white pixels
    return white_pixels[0], white_pixels[-1], white_pixels[-1][1] - white_pixels[0][1]

def findMinMaxLengthY(ROI):
    '''
    Given a thresholded nparray ROI, find the points corresponding to minimum y, maximum y and the vertical length as an 3-tuple.
    '''
    # Find the coordinates of the white pixels in the vertical ROI
    white_pixels = np.column_stack(np.where(ROI == 255))
    
    
    if len(white_pixels) <= 1:
        return None  # No white pixels found
    white_pixels = sorted(white_pixels, key=lambda y: y[0])
    # Get the maximum x-coordinate (column index) of the white pixels
    return white_pixels[0], white_pixels[-1], white_pixels[-1][0] - white_pixels[0][0]


def convertUnits(array, conversion):
    for i in range(len(array)):
        array[i] = array[i] * conversion



