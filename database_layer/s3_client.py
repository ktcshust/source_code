# s3_client.py
import boto3
from .db_config import settings

s3 = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
)

def upload_report(file_path: str, file_name: str):
    s3.upload_file(file_path, settings.s3_bucket, file_name)
    return f"s3://{settings.s3_bucket}/{file_name}"
# boto3 / aioboto3 client
