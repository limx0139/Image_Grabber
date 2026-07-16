import cv2


def drawOverlay(self, image, fps, flag_state):
    """
    Superimposes an overlay over the false color image.
    """
    mode = self._imager.getActiveOperationMode()

    opticsText = mode.getOpticsText()
    if len(opticsText) != 0:
        opticsText = ' {}'.format(opticsText)

    # Overlay text
    text = [
            'i: MoveIn', 
            'o: MoveOut',
            'q: Quit']

    # Text font face
    thickness = 1
    line_margin = 10

    # Overlay position
    x = image.shape[1] - 275
    y = 25

    # Draw overlay
    for i, line in enumerate(text):
        line_height = cv2.getTextSize(line, self.FONT_FACE, self.FONT_SIZE, thickness)[0][1]
        position    = (x, y + i * (line_height + line_margin))

        cv2.putText(image, line, position, self.FONT_FACE, self.FONT_SIZE, self.BLACK, thickness+1, lineType = cv2.LINE_AA)
        cv2.putText(image, line, position, self.FONT_FACE, self.FONT_SIZE, self.GREEN, thickness, lineType = cv2.LINE_AA)
    