# DICOM to MP4 Lambda Function

This AWS Lambda function converts DICOM files to MP4 format.

## Requirements

- Python 3.8+
- Required Python packages:
  ```
  dcm2mp4
  ```

## Usage

Convert a DICOM file to MP4:

```bash
# Using curl
curl -X POST https://your-api-gateway-url/prod/convert \
  -H "Content-Type: application/json" \
  -d "{
    \"dicom_data\": \"$(base64 your_file.dcm)\""
  }"
```

Python example:
```python
import base64
import requests

# Read and encode DICOM file
with open('your_file.dcm', 'rb') as f:
    dicom_data = base64.b64encode(f.read()).decode('utf-8')

# Send to Lambda
response = requests.post(
    'https://your-api-gateway-url/prod/convert',
    json={'dicom_data': dicom_data}
)

# Save MP4 file
if response.status_code == 200:
    mp4_data = response.json()['mp4_data']
    with open('output.mp4', 'wb') as f:
        f.write(base64.b64decode(mp4_data))
```

## Health Check
```bash
curl -X POST https://your-api-gateway-url/prod/convert \
  -H "Content-Type: application/json" \
  -d '{"ping": true}'
```

## Testing Ping-Pong

1. Using curl:
```bash
# Test ping with curl
curl -X POST https://your-api-gateway-url/prod/convert \
  -H "Content-Type: application/json" \
  -d '{"ping": true}'

# Expected response:
# {
#   "statusCode": 200,
#   "body": {
#     "message": "pong",
#     "status": "healthy"
#   }
# }
```

2. Using Python:
```python
import requests

# Test ping
response = requests.post(
    'https://your-api-gateway-url/prod/convert',
    json={'ping': True}
)

print(response.json())
```

3. Using local test:
```bash
# If using Docker
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"ping": true}'

# If using AWS CLI
aws lambda invoke \
  --function-name your-function-name \
  --payload '{"ping": true}' \
  response.json && cat response.json
```

## Testing with Docker Compose

1. Start the service:
```bash
docker-compose up --build
```

2. Test the ping endpoint (in another terminal):
```bash
# Using curl
curl -X POST http://localhost:8080/2015-03-31/functions/function/invocations \
  -d '{"ping": true}'

# Using the test script
python test_ping.py --local

# Expected response:
# {
#   "statusCode": 200,
#   "body": {
#     "message": "pong",
#     "status": "healthy"
#   }
# }
```

3. Test file conversion:
```bash
# Using curl
curl -X POST http://localhost:8080/2015-03-31/functions/function/invocations \
  -H "Content-Type: application/json" \
  -d "{
    \"dicom_data\": \"$(base64 your_file.dcm)\"
  }"
```

Note: Replace `your-api-gateway-url` with your actual API Gateway URL
