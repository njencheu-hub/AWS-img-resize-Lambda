# This script is for an AWS Lambda function that:
# 1. Takes a request for an image and size
# 2. Checks if the resized image already exists
# 3. If not, resizes the image using Pillow
# 4. Uploads the new version to S3
# 5. Sends back a public URL to the resized image

# Perfect for building a serverless image resizer API 
import json # This lets us read and write JSON data.
import os   # This lets us read environment variables, like getting the bucket name stored in AWS.
import boto3    # boto3 is how Python talks to AWS services (like S3 = file storage in the cloud).
import botocore # This helps us catch errors when things go wrong using boto3.
import PIL  
from PIL import Image  # We use this to work with images (like opening and resizing them).
from io import BytesIO  #  This lets us treat image data (like the raw bytes of a file) as a file-like object in memory.

s3 = boto3.resource('s3')
# This sets up a connection to S3 so we can read and write files in buckets (AWS folders).

def is_resized_image_exists(bucket_name, key, size):
    # We're creating a function that checks if a resized version of the image already exists.
    try:
        s3.Object(bucket_name=bucket_name, key='{size}_{key}'.format(size=size, key=key)).load()
        #  Try to load the file with a new name like '200x200_dog.jpg'. If it exists, great.
    except botocore.exceptions.ClientError:
        return None
    #  If it doesn't exist, catch the error and return None.


def resize_image(bucket_name, key, size):
    # This function takes the image and makes a new smaller version of it.
    size_split = size.split('x')
    # For example, if size = "200x200", this becomes ['200', '200'].
    try:
        s3.Object(bucket_name=bucket_name, key=key).load()
        is_resized_image_exists(bucket_name, key, size)
        # First, check if the original image exists and if the resized one already exists.
    except botocore.exceptions.ClientError:
        return None
    # If the original image doesn’t exist, stop the function and return None.
    obj = s3.Object(bucket_name=bucket_name, key=key)
    # Get the image from the S3 bucket.
    obj_body = obj.get()['Body'].read()
    #  Read the image bytes (raw data).
    img = Image.open(BytesIO(obj_body))
    # Open the image from bytes using PIL.
    img = img.resize((int(size_split[0]), int(size_split[1])), Image.LANCZOS)
    # Resize the image to the new dimensions with high-quality scaling.
    buffer = BytesIO()
    # Create a temporary "file" in memory to store the new image.
    img.convert('RGB').save(buffer, 'JPEG')
    # Convert the image to JPEG format and save it to the buffer.
    buffer.seek(0)
    # Reset the "pointer" to the start of the buffer so it can be read again.
    resized_key='{size}_{key}'.format(size=size, key=key)
    # Create a new file name like '200x200_cat.jpeg'.
    obj = s3.Object(bucket_name=bucket_name, key=resized_key)
    # Create a new S3 object with this new name.
    obj.put(Body=buffer, ContentType='image/jpeg')
    # Upload the resized image back to the S3 bucket.
    return "https://{bucket}.s3.amazonaws.com/{resized_key}".format(bucket=bucket_name, resized_key=resized_key)
    #  Return the full URL to the resized image so it can be accessed online.

def lambda_handler(event, context):
    # This is the function AWS Lambda runs when someone makes a request.
    key = event['queryStringParameters'].get('key', None)
    size = event['queryStringParameters'].get('size', None)
    # It looks in the request for two things:
    # 1. key: the name of the image (like "cat.jpeg")
    # 2. size: the new dimensions (like "200x200")

    image_s3_url = resize_image(os.environ['BUCKET_NAME'], key, size)
    # Get the bucket name from environment variables and call the resize function.

    if image_s3_url is None:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'message': 'Image not found',
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Image resized successfully',
            'resized_image_url': image_s3_url
        }),
        'headers': {
            'Content-Type': 'application/json'
        }
    }

    # Return the image URL with status code 301 (redirect — meaning: “go here!”)