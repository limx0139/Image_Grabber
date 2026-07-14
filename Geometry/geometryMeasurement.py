



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
        # print(f"Measuring vertical geometry for ROI {x+1}...")
        # print(verticalGeometry)
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

def measureHorizontalGeometry(horizontalGeometry, edged, numHorizontalROIs):
    '''
    Measure the lengths in each horizontal ROI and return the lengths as a np list. The lengths are measured in pixels.
    '''
    num_rows, num_cols = edged.shape[:2]
    height = num_rows // numHorizontalROIs
    coords = []
    for y in range(numHorizontalROIs):
        # print(f"Measuring horizontal geometry for ROI {y+1}...")
        # print(horizontalGeometry)
        # Extract the horizontal ROI from the edged image
        if y == numHorizontalROIs - 1:  # Last ROI may be taller due to integer division
            horizontal_ROI = edged[y * height:num_rows, :]
        else:
            horizontal_ROI = edged[y * height:y * height + height, :]
        z = findMinMaxLengthX(horizontal_ROI)
        if z is None:
            horizontalGeometry[y] = 0
            coords.append(None)
            continue
        (y1, min_x), (y2, max_x), length = z

        y1 = y * height + y1  # Calculate the y position for drawing
        y2 = y * height + y2
        horizontalGeometry[y] = length
        print(((min_x, y2), (max_x, y1), length))
        coords.append(((min_x, y2), (max_x, y1), length))  # Store min_x, max_x, and y position for drawing
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

def findMinMaxLengthX(ROI):
    '''
    Find the maximum x-coordinate of the white pixels in the vertical ROI.
    '''
    # Find the coordinates of the white pixels in the vertical ROI
    white_pixels = np.column_stack(np.where(ROI == 255))
    
    
    if len(white_pixels) <= 1:
        return None  # No white pixels found
    white_pixels = sorted(white_pixels, key=lambda x: x[1])
    # Get the maximum x-coordinate (column index) of the white pixels
    return white_pixels[0], white_pixels[-1], white_pixels[-1][1] - white_pixels[0][1]

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

