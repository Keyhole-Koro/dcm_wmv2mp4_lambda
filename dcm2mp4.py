import os
import pydicom
import cv2
import numpy as np
from pathlib import Path
import subprocess
import tempfile
import platform

def get_ffmpeg_path():
    """Get FFmpeg executable path based on OS."""
    # Check for custom FFmpeg path in environment variable
    custom_path = os.getenv('FFMPEG_PATH')
    if custom_path:
        return custom_path

    # Default paths based on OS
    if platform.system() == 'Windows':
        # Check common Windows installation paths
        paths = [
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            'ffmpeg.exe'  # If in PATH
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return 'ffmpeg.exe'  # Default to PATH
    else:
        # Linux/Unix systems
        return '/opt/ffmpeg/ffmpeg'

def get_crf_value(quality='normal'):
    """Get CRF value based on quality preset."""
    crf_values = {
        'low': 28,    # Lower quality
        'normal': 23, # Default quality
        'high': 18    # Higher quality
    }
    return crf_values.get(quality, crf_values['normal'])

def save_frame(frame, output_dir, frame_index, prefix='frame'):
    """Save a single frame to the specified directory."""
    frame_path = output_dir / f"{prefix}_{frame_index:06d}.png"
    cv2.imwrite(str(frame_path), frame)
    return frame_path

def convert_dicom_to_mp4(input_path, output_path, framerate=30, quality='normal'):
    """
    Convert DICOM files to MP4 video using FFmpeg.
    
    Args:
        save_interval (int, optional): Save every Nth frame as image. None means don't save.
        save_dir (str, optional): Directory to save frames. Required if save_interval is set.
    """
    ffmpeg_path = get_ffmpeg_path()
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
            
            # Normalize pixel values to 8-bit range
            frame = cv2.normalize(frame.astype(np.float32), None, 0, 255, cv2.NORM_MINMAX)
            frame = np.clip(frame, 0, 255).astype(np.uint8)

            # Handle grayscale and color images properly
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # DICOM stores in RGB, convert to BGR for OpenCV
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            # Save frame to temp dir for video creation
            temp_frame_path = save_frame(frame, temp_dir, frame_index)
            
            if frame_index % 10 == 0:
                print(f"Processed frame {frame_index}/{ds.NumberOfFrames}")
        
        # Get CRF value
        crf_value = get_crf_value(quality)
        
        # Get frame dimensions
        first_frame = ds.pixel_array[0]
        height, width = first_frame.shape[:2]
        
        # Calculate dimensions that are divisible by 2
        new_width = width if width % 2 == 0 else width - 1
        new_height = height if height % 2 == 0 else height - 1
        
        # Encode video using FFmpeg
        ffmpeg_cmd = [
            ffmpeg_path, '-y',
            '-framerate', str(framerate),
            '-i', str(temp_dir / 'frame_%06d.png'),
            '-c:v', 'libx264 -preset medium',
            '-crf', str(crf_value),
            '-preset', 'medium',
            '-vf', "colorspace=bt709:iall=bt709:fast=1",
            '-x264-params', 'colorprim=bt709:transfer=bt709:colormatrix=bt709' \
            '-pix_fmt', 'yuv420p',
            '-loglevel', 'debug',
            str(output_path)
        ]
        
        print(f"Video dimensions: {width}x{height} -> {new_width}x{new_height}")
        print("Running FFmpeg command:", " ".join(ffmpeg_cmd))
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        print("FFmpeg errors:", result.stderr)
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg command failed with return code {result.returncode}")
        
        print(f"Successfully converted {input_path} to {output_path}")

        # Validate the output MP4 file
        validate_cmd = [
            ffmpeg_path, '-v', 'error', '-i', str(output_path),
            '-f', 'null', '-'
        ]
        validate_result = subprocess.run(validate_cmd, capture_output=True, text=True)
        if validate_result.returncode != 0:
            print(f"Validation errors for {output_path}: {validate_result.stderr}")
        else:
            print(f"Validation successful for {output_path}")

if __name__ == "__main__":
    input_file = "output/A0001.dcm"
    output_files = {
        'low': "output/video_low.mp4",
        #'normal': "output/video_normal.mp4",
        #'high': "output/video_high.mp4"
    }
    
    # Example usage with frame saving
    for quality, output_file in output_files.items():
        try:
            convert_dicom_to_mp4(
                input_file,
                output_file,
                quality=quality,
            )
        except Exception as e:
            print(f"Error converting to {quality} quality: {str(e)}")
            import traceback
            traceback.print_exc()
