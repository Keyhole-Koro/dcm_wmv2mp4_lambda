import os
import pydicom
import cv2
import numpy as np
from pathlib import Path
import subprocess
import tempfile

def convert_dicom_to_mp4(input_path, output_path, framerate=30, bitrate=10000000):
    """Convert DICOM files to MP4 video using FFmpeg."""
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ds = pydicom.dcmread(input_path)
    print(f"DICOM info - Rows: {ds.Rows}, Columns: {ds.Columns}")
    
    if "PixelData" not in ds or not hasattr(ds, "NumberOfFrames"):
        raise ValueError("DICOM file does not contain valid video data")

    # Create temporary directory for frames
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        
        # Write frames as PNG files
        for frame_index in range(ds.NumberOfFrames):
            frame = ds.pixel_array[frame_index]
            
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            else:
                frame = frame.reshape((ds.Rows, ds.Columns))
                frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            
            frame_path = temp_dir / f"frame_{frame_index:06d}.png"
            cv2.imwrite(str(frame_path), frame)
            if frame_index % 10 == 0:
                print(f"Processed frame {frame_index}/{ds.NumberOfFrames}")
        
        # Encode video using FFmpeg
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-framerate', str(framerate),
            '-i', str(temp_dir / 'frame_%06d.png'),
            '-c:v', 'libx264',
            '-b:v', f'{bitrate}',
            '-maxrate', f'{bitrate*1.5}',
            '-bufsize', f'{bitrate*2}',
            '-preset', 'slow',
            '-crf', '18',
            str(output_path)
        ]
        
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        print(f"Successfully converted {input_path} to {output_path}")

if __name__ == "__main__":
    input_file = "materials/A0000.dcm"
    output_file = "output/video.mp4"
    
    try:
        convert_dicom_to_mp4(input_file, output_file, bitrate=10000000)
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()