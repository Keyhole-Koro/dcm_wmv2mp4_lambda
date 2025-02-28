import os
import subprocess
import pydicom
import glob
from pathlib import Path
import shutil
import sys
import cv2
import numpy as np

def check_ffmpeg():
    """Check if FFmpeg is installed."""
    if not shutil.which('ffmpeg'):
        print("Error: FFmpeg not found. Installing ffmpeg...")
        try:
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'ffmpeg'], check=True)
        except subprocess.CalledProcessError:
            print("Failed to install FFmpeg. Please install it manually:\nsudo apt-get install ffmpeg")
            exit(1)

def convert_wmv_to_mp4(input_wmv, output_mp4):
    """Convert WMV to MP4 using FFmpeg."""
    check_ffmpeg()
    output_path = Path(output_mp4).parent
    output_path.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        'ffmpeg', '-i', str(input_wmv),
        '-c:v', 'libx264', '-crf', '23', '-preset', 'fast',
        '-c:a', 'aac', '-b:a', '128k', str(output_mp4)
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Converted {input_wmv} to {output_mp4}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting file: {e}")
        exit(1)

def convert_dcm_to_mp4(input_dcm, output_mp4, framerate=30):
    """Convert DCM (DICOM video or image sequence) to MP4 using OpenCV."""
    check_ffmpeg()
    output_path = Path(output_mp4).parent
    output_path.mkdir(parents=True, exist_ok=True)
    
    ds = pydicom.dcmread(input_dcm)
    
    try:
        if "PixelData" in ds and hasattr(ds, "NumberOfFrames"):
            # Create a video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(str(output_mp4), fourcc, framerate, (ds.Columns, ds.Rows), isColor=True)
            
            for frame_index in range(ds.NumberOfFrames):
                frame = ds.pixel_array[frame_index]
                expected_size = ds.Rows * ds.Columns
                if frame.size != expected_size:
                    raise ValueError(f"Unexpected frame size: {frame.size}, expected: {expected_size}")
                frame = frame.reshape((ds.Rows, ds.Columns))  # Ensure correct shape
                frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)  # Convert to BGR format
                video_writer.write(frame)
            
            video_writer.release()
        
        else:
            frames_dir = Path("frames")
            frames_dir.mkdir(exist_ok=True)
            
            for i, frame in enumerate(ds.pixel_array):
                expected_size = ds.Rows * ds.Columns
                if frame.size != expected_size:
                    raise ValueError(f"Unexpected frame size: {frame.size}, expected: {expected_size}")
                frame = frame.reshape((ds.Rows, ds.Columns))  # Ensure correct shape
                frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                filename = frames_dir / f"frame_{i:04d}.png"
                cv2.imwrite(str(filename), frame)
            
            cmd = [
                'ffmpeg', '-framerate', str(framerate), '-i', str(frames_dir / "frame_%04d.png"),
                '-c:v', 'libx264', str(output_mp4)
            ]
            subprocess.run(cmd, check=True)
            
            for file in frames_dir.glob("*.png"):
                file.unlink()
            frames_dir.rmdir()
        
        print(f"Converted {input_dcm} to {output_mp4}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting file: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert.py <input_file> <output_file>")
        exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    if input_file.suffix.lower() == ".wmv":
        convert_wmv_to_mp4(input_file, output_file)
    elif input_file.suffix.lower() == ".dcm":
        convert_dcm_to_mp4(input_file, output_file)
    else:
        print("Unsupported file format. Please provide a .wmv or .dcm file.")