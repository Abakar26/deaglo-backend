import logging
import os
from logging import getLogger

from boto3 import Session


class S3:
    logger = getLogger()

    def __init__(self, session: Session, bucket_name: str):
        self.client = session.client("s3")
        self.bucket_name = bucket_name

    def upload(self, file, path: str, bucket_name: str | None = None):
        """
        Upload a file to S3
        """
        s3_bucket = bucket_name if bucket_name else self.bucket_name
        self.client.upload_fileobj(file, s3_bucket, path)
        self.logger.info(f"Uploaded file to s3://{s3_bucket}/{path}")

    def download(
        self, s3_object_path: str, output_path: str, bucket_name: str | None = None
    ):
        """
        Download a file from S3
        """
        if os.path.exists(output_path):
            self.logger.info(f"Removing existing file at {output_path}...")
            os.remove(output_path)
        logging.info(f"Downloading file from S3 to {output_path}...")
        s3_bucket = bucket_name if bucket_name else self.bucket_name
        self.client.download_file(
            s3_bucket,
            s3_object_path,
            output_path,
        )
        self.logger.info(f"Downloaded file from s3://{s3_bucket}/{s3_object_path}")
