import boto3

from .s3 import S3
from .ses import SES
from .sqs import SQS
from .ssm import SSM


class AWSManager:
    def __init__(
        self, aws_access_key_id: str, aws_secret_access_key: str, region_name: str
    ):
        self.client = (
            boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name,
            )
            if aws_secret_access_key and aws_access_key_id
            else boto3.Session(region_name=region_name)
        )
        self.ssm = SSM(self.client)
        self.ses = None
        self.sqs = None
        self.s3 = None

    def configure(
        self,
        system_email: str,
        queue_url: str,
        bucket_name: str,
        environment: str,
        ci: bool,
    ):
        self.ses = SES(self.client, system_email, environment, ci)
        self.sqs = SQS(self.client, queue_url)
        self.s3 = S3(self.client, bucket_name)
