import pydicom
import numpy as np
import cv2
from pathlib import Path

def convert_dicom_to_mp4(input_path, output_path, fps=30):
    """Convert DICOM file to MP4 video."""
    # Read DICOM file
    dicom = pydicom.dcmread(input_path)
    
    # Extract pixel array
    pixels = dicom.pixel_array
    
    # Normalize pixel values to 0-255 range
    if pixels.dtype != np.uint8:
        pixels = ((pixels - pixels.min()) * 255.0 / 
                 (pixels.max() - pixels.min())).astype(np.uint8)
    
    # Get dimensions
    if len(pixels.shape) == 3:
        frames, height, width = pixels.shape
    else:
        raise ValueError("DICOM file does not contain multi-frame data")
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    # Write frames
    for frame in pixels:
        # Convert grayscale to BGR if needed
        if len(frame.shape) == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        out.write(frame)
    
    # Release resources
    out.release()
    
    return output_path
