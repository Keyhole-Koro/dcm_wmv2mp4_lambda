import boto3
import argparse
import json
from pathlib import Path

def upload_and_process(file_path, bucket_name, aws_region='us-east-1'):
    """Upload DICOM file and trigger Lambda processing"""
    
    # Initialize AWS clients
    s3 = boto3.client('s3', region_name=aws_region)
    lambda_client = boto3.client('lambda', region_name=aws_region)
    
    # Upload file to S3
    file_path = Path(file_path)
    s3_key = f"uploads/{file_path.name}"
    print(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}")
    
    s3.upload_file(str(file_path), bucket_name, s3_key)
    
    # Create test event
    test_event = {
        "Records": [{
            "s3": {
                "bucket": {"name": bucket_name},
                "object": {"key": s3_key}
            }
        }]
    }
    
    # Invoke Lambda function
    print("Invoking Lambda function...")
    response = lambda_client.invoke(
        FunctionName='dicom-to-mp4',
        InvocationType='RequestResponse',
        Payload=json.dumps(test_event)
    )
    
    # Parse response
    result = json.loads(response['Payload'].read())
    print("\nLambda Response:")
    print(json.dumps(result, indent=2))
    
    if result['statusCode'] == 200:
        body = json.loads(result['body'])
        print(f"\nSuccess! Output file: {body['output']}")
    else:
        print(f"\nError: {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Upload DICOM file and process with Lambda')
    parser.add_argument('file', help='Path to DICOM file')
    parser.add_argument('bucket', help='S3 bucket name')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    upload_and_process(args.file, args.bucket, args.region)
