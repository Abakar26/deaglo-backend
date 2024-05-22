import json
import os
import sys
from dotenv import load_dotenv

from api_gateway.aws import AWSManager
from api_gateway.fenics import FenicsApiClient

# Load environment variables
load_dotenv()


# Function to safely retrieve environment variable or default
def get_env_var(var_name, default=None, required=False):
    value = os.environ.get(var_name, default)
    if required and value is None:
        raise EnvironmentError(
            f"Required environment variable '{var_name}' is missing."
        )
    return value


# Retrieve AWS credentials and region
AWS_ACCESS_KEY_ID = get_env_var("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_env_var("AWS_SECRET_ACCESS_KEY")
AWS_REGION = get_env_var(
    "AWS_REGION", "us-east-2"
)  # Default to us-east-2 if not specified

# Django and environment settings
DJANGO_DEBUG = bool(eval(get_env_var("DEBUG", "False")))
DJANGO_TESTING = "test" in sys.argv
ENVIRONMENT = get_env_var("ENVIRONMENT", required=True)
CI = bool(eval(get_env_var("CI", "False")))

if ENVIRONMENT not in ["dev", "staging", "prod", "demo"]:
    raise ValueError(
        f"Invalid environment '{ENVIRONMENT}'. Must be one of 'dev', 'staging',demo or 'prod'."
    )

# Initialize AWS Manager
AWS = AWSManager(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)


# Retrieve configuration from AWS SSM
def get_ssm_config(path):
    value = AWS.ssm.get_param(path, with_decryption=True)
    if value is None:
        raise ValueError(f"SSM parameter not found for path: {path}")
    return json.loads(value)


db_ssm_path = f"/deaglo/platform/{ENVIRONMENT}/database"
settings_ssm_path = f"/deaglo/api-gateway/{ENVIRONMENT}/settings"

DB_STORE = get_ssm_config(db_ssm_path)
SETTINGS_STORE = get_ssm_config(settings_ssm_path)

# Database Configuration
DB_HOST = get_env_var("DB_HOST", default=DB_STORE["DB_HOST"])
DB_PASSWORD = get_env_var("DB_PASSWORD", default=DB_STORE["DB_PASSWORD"])
DB_PORT = int(get_env_var("DB_PORT", default=DB_STORE["DB_PORT"]))
DB_NAME = get_env_var("DB_NAME", default=DB_STORE["DB_NAME"])
DB_USER = get_env_var("DB_USER", default=DB_STORE["DB_USER"])

# Django and token-related configuration
SYSTEM_EMAIL = SETTINGS_STORE["SYSTEM_EMAIL"]
DJANGO_SECRET_KEY = SETTINGS_STORE["SECRET_KEY"]
ACCESS_TTL = int(SETTINGS_STORE["ACCESS_TTL"])  # Days Access Token is valid
REFRESH_TTL = int(SETTINGS_STORE["REFRESH_TTL"])  # Days Refresh Token is valid

SIMULATION_QUEUE_URL = SETTINGS_STORE[
    "SIMULATION_QUEUE_URL"
]  # URL of SQS simulation queue
BUCKET_NAME = SETTINGS_STORE["BUCKET_NAME"]

# AWS Utilities setup
AWS.configure(SYSTEM_EMAIL, SIMULATION_QUEUE_URL, BUCKET_NAME, ENVIRONMENT, CI)

# LinkedIn OAuth Parameters
LINKEDIN_CLIENT_ID = SETTINGS_STORE["LINKEDIN_CLIENT_ID"]
LINKEDIN_CLIENT_SECRET = SETTINGS_STORE["LINKEDIN_CLIENT_SECRET"]
LINKEDIN_REDIRECT_URI_AUTH = SETTINGS_STORE["LINKEDIN_REDIRECT_URI_AUTH"]
LINKEDIN_REDIRECT_URI_LINK = SETTINGS_STORE["LINKEDIN_REDIRECT_URI_LINK"]

# Fenics Client Setup
FENICS_CLIENT = FenicsApiClient(
    username=SETTINGS_STORE["FENICS_USERNAME"],
    password=SETTINGS_STORE["FENICS_PASSWORD"],
    api_url=SETTINGS_STORE["FENICS_PRICING_API_URL"],
)
