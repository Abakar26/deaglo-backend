import json
from boto3 import Session
from logging import getLogger

from api_gateway.exceptions import GenericAPIError


class SQS:
    logger = getLogger()

    def __init__(self, session: Session, queue_url: str):
        self.client = session.client("sqs")
        self.queue_url = queue_url

    def enqueue(self, data: dict, message_group_id: str) -> bool:
        try:
            _data = json.dumps(data)
            response = self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=_data,
                MessageGroupId=message_group_id,
            )
            return response["ResponseMetadata"]["HTTPStatusCode"] == 200
        except Exception as e:
            raise GenericAPIError(f"Failed to enqueue message: {e}", code=500)
