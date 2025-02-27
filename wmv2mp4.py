import cv2

input_file = "materials/A0.wmv"
output_file = "output/video1.mp4"

# Open the video file
cap = cv2.VideoCapture(input_file)

# Get video properties
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object (MP4 using H.264 codec)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' for AVI
out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    out.write(frame)

cap.release()
out.release()
cv2.destroyAllWindows()
