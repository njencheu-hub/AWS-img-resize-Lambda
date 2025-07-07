# AWS Lambda Image Resizer
A serverless image resizing microservice using **AWS Lambda**, **Amazon S3**, and **Python (Pillow)**.  

## Table of Contents

- [Overview](#aws-lambda-image-resizer)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Input Example](#input-example)
- [Output Example](#output-example)
- [Testing Tips](#testing-tips)
- [IAM Policy Example](#iam-policy-example)
- [Sample Image Output](#sample-image-output)

## Overview

This Lambda function accepts an image key and a target size via API request, resizes the image in-memory, and stores the new version back to S3.

---

## Features

- Resize JPEG images dynamically via API call
- In-memory image processing with BytesIO (no temp files)
- High-quality resizing using Pillow with Image.LANCZOS
- Skips processing if resized image already exists
- Returns a clean JSON response with a public S3 URL
- Designed for API Gateway, serverless, and pay-per-use workloads

---

## Tech Stack

- **Language**: Python 3.9+
- **Cloud Services**: AWS Lambda, Amazon S3
- **Libraries**: boto3, botocore, Pillow, io

---

## Folder Structure

plaintext
lambda_function.py              # Main handler with resizing logic
python/lib/python3.9/...        # Lambda layer (with Pillow)


## Input Example

Send a request to the Lambda function using this format (e.g., via API Gateway):

json
{
  "queryStringParameters": {
    "key": "cat.jpeg",
    "size": "200x200"
  }
}

Or, if testing directly in the Lambda console:

json
{
    "key": "cat.jpeg",
    "size": "200x200"
}


## Output Example

json
{
  "statusCode": 200,
  "body": {
    "message": "Image resized successfully",
    "resized_image_url": "https://your-bucket-name.s3.amazonaws.com/200x200_cat.jpeg"
  },
  "headers": {
    "Content-Type": "application/json"
  }
}


## Testing Tips

- **Upload your test image** (cat.jpeg) to your S3 bucket.
- **Set BUCKET_NAME** as an environment variable in your Lambda configuration.
- **Ensure your Lambda's IAM role includes the following permissions:**
  - s3:GetObject
  - s3:PutObject
  - s3:ListBucket

## IAM Policy Example

json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::your-bucket-name",
    "arn:aws:s3:::your-bucket-name/*"
  ]
}


## Sample Image Output

[View resized example](https://imgs-resize-bucket.s3.amazonaws.com/200x200_cat.jpeg)


