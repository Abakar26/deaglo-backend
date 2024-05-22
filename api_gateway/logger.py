import logging

import boto3


class CloudWatchHandler(logging.Handler):
    """
    Custom logging handler for sending log messages to AWS CloudWatch Logs.

    This module defines a custom logging handler, `CloudWatchHandler`, which extends
    the `logging.Handler` class. The handler is designed to send log messages to AWS
    CloudWatch Logs, ensuring the existence of the specified log group and log stream.

    Classes:
        CloudWatchHandler(logging.Handler):
            Custom logging handler for CloudWatch Logs.

            Args:
                log_group_name (str): The name of the CloudWatch log group.
                log_stream_name (str): The name of the CloudWatch log stream.
                aws_region_name (str): The AWS region name where the log group resides.
                *args, **kwargs: Additional arguments for the logging.Handler class.

    """

    def __init__(
        self, log_group_name, log_stream_name, aws_region_name, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.aws_region_name = aws_region_name
        self.client = boto3.client("logs", region_name=self.aws_region_name)

        # Ensure log group and log stream exist
        self.ensure_log_group_and_stream_exist()

    def ensure_log_group_and_stream_exist(self):
        """
        Ensures that the specified log group and log stream exist in CloudWatch Logs.
               If they do not exist, it creates them and sets a default retention policy.

        """
        # Check if log group exists
        if not self.client.describe_log_groups(logGroupNamePrefix=self.log_group_name)[
            "logGroups"
        ]:
            self.client.create_log_group(logGroupName=self.log_group_name)
            self.client.put_retention_policy(
                logGroupName=self.log_group_name, retentionInDays=14
            )

        if not self.client.describe_log_streams(
            logGroupName=self.log_group_name,
            logStreamNamePrefix=self.log_stream_name,
        )["logStreams"]:
            sanitized_stream_name = self.log_stream_name.replace(":", "-").replace(
                "*", "_"
            )
            self.client.create_log_stream(
                logGroupName=self.log_group_name,
                logStreamName=sanitized_stream_name,
            )

    def emit(self, record):
        """
        Sends log messages to CloudWatch Logs as log events.
                Converts log records into CloudWatch Logs format and publishes the events.
        """
        log_message = self.format(record)

        # Publish log event
        self.client.put_log_events(
            logGroupName=self.log_group_name,
            logStreamName=self.log_stream_name,
            logEvents=[
                {
                    "timestamp": int(record.created * 1000),
                    "message": log_message,
                },
            ],
        )
