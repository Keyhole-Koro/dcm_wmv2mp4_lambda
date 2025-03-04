import json
import base64
from utils import convert_dicom_to_mp4
from pathlib import Path
import tempfile

def handle_ping():
    """Handle ping request to check if the service is responsive."""
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'pong',
            'status': 'healthy'
        })
    }

def handle_conversion(dicom_data):
    """Convert DICOM data to MP4."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        
        # Save incoming DICOM data
        input_path = temp_dir / "input.dcm"
        with open(input_path, 'wb') as f:
            f.write(base64.b64decode(dicom_data))
        
        # Convert to MP4
        output_path = temp_dir / "output.mp4"
        convert_dicom_to_mp4(
            input_path=str(input_path),
            output_path=str(output_path),
            fps=30
        )
        
        # Read and encode MP4
        with open(output_path, 'rb') as f:
            mp4_data = base64.b64encode(f.read()).decode('utf-8')
            
        return mp4_data

def lambda_handler(event, context):
    """AWS Lambda handler for DICOM to MP4 conversion."""
    try:
        # Check if this is a ping request
        if event.get('ping'):
            return handle_ping()

        # Handle DICOM conversion
        if 'dicom_data' in event:
            mp4_data = handle_conversion(event['dicom_data'])
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'message': 'Conversion successful',
                    'mp4_data': mp4_data
                })
            }
        
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Invalid request. Send DICOM data as base64 in dicom_data field.'
            })
        }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
