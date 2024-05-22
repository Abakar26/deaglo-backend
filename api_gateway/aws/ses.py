import textwrap
from logging import getLogger
from typing import Literal

import html2text
from boto3 import Session
from botocore.exceptions import ClientError


class SES:
    logger = getLogger()

    def __init__(self, session: Session, system_email: str, environment: str, ci: bool):
        self.client = session.client("ses")
        self.system_email = system_email
        self.environment = environment
        self.ci = ci

    def send_email(
        self,
        subject: str,
        body: str,
        recipient: str,
        mail_type: Literal["Html", "Text"],
        source=None,
    ):
        """
        Send an email using AWS Simple Email Service (SES).

        This function sends an email through AWS SES with the specified subject, body,
        recipient email address, and email format (HTML or plain text).

        Parameters:
            subject (str): The subject of the email.
            body (str): The body of the email.
            recipient (str): The email address of the recipient.
            mail_type (Literal["Html", "Text"]): The type of email format, either "Html" or "Text".
            source (str): The email address of the sender. Defaults to SYSTEM_EMAIL.

        Returns:
            bool: True if the email is sent successfully, False otherwise.

        Raises:
            ValueError: If mail_type is not one of ["Html", "Text"].

        Example:
            send_email(
                subject='Greetings',
                body='Hello, welcome to our platform!',
                recipient='user@example.com',
                mail_type='Html'
            )

        """
        if mail_type not in ["Text", "Html"]:
            raise ValueError("Only Html or Text is allowed as mail_type")
        message = {"Subject": {"Data": subject}, "Body": {mail_type: {"Data": body}}}
        source = self.system_email if source is None else source
        try:
            if (self.environment == "dev") or self.ci:
                text_content = html2text.html2text(body)
                wrapped_content = textwrap.fill(text_content, width=80)
                self.logger.info(
                    f"\n\nEmail sent! {wrapped_content}\nsource {source}\ndestination {recipient}\n\n"
                )
                return True
            response = self.client.send_email(
                Source=source, Destination={"ToAddresses": [recipient]}, Message=message
            )
            status_code = response["ResponseMetadata"]["HTTPStatusCode"]
            if status_code == 200:
                self.logger.info(f"Email sent! Message ID: {response['MessageId']}")
                return True
            raise Exception(response)
        except ClientError as e:
            self.logger.error(f"Error sending email: {e.response['Error']['Message']}")
        except Exception as e:
            self.logger.error(e.args)

        return False
