from boto3 import Session


class SSM:
    def __init__(self, session: Session):
        self.client = session.client("ssm")

    def get_param(self, name: str, with_decryption: bool = False):
        return self.client.get_parameter(Name=name, WithDecryption=with_decryption)[
            "Parameter"
        ]["Value"]
