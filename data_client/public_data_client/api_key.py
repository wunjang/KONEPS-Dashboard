import os
from dotenv import load_dotenv
import boto3

# TODO. 환경에 따라 설치해야 하는 라이브러리가 다른데 전부 설치하고 있다
def get_api_key():
    load_dotenv()
    api_key = os.getenv('PUBLIC_DATA_API_KEY')

    if api_key:
        return api_key
    else:
        ssm = boto3.client('ssm', region_name='ap-southeast-2')
        parameter = ssm.get_parameter(Name='/api_key/public_data', WithDecryption=True)
        return parameter['Parameter']['Value']