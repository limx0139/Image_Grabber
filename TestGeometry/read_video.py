import cv2

# Load the video file
cap = cv2.VideoCapture("ForgingVideos/video2.mp4")

# Check if the video opened correctly
if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Read and display video frames
while True:
    ret, frame = cap.read()

    if not ret:
        break   # No more frames -> exit loop

    cv2.imshow("Video", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()