'''
适用于阿里云ECS通过“实例RAM角色”访问OSS的情形。
需设置以下环境变量：
RAM_ROLE_NAME：实例RAM角色名称
BUCKET_NAME：Bucket名称
BUCKET_ENDPOINT：OSS Bucket的外网Endpoint e.g.'oss-cn-hongkong.aliyuncs.com'
'''
import oss2
from alibabacloud_credentials.client import Client
from alibabacloud_credentials.models import Config
from oss2 import CredentialsProvider
from oss2.credentials import Credentials
import os

class OssBucket:
    def __init__(self, bucket):
        self.bucket = bucket

    def get_object_to_file(self, object_key, local_file):
        self.bucket.get_object_to_file(object_key, local_file)

    # --- Helper function to read object content from OSS ---
    def read_object_content(self, object_key, encoding='utf-8'):
        """Reads an object's content from OSS and returns it as a string."""
        try:
            # Get object in streaming mode, but read fully for small files
            result = self.bucket.get_object(object_key)
            content_bytes = result.read()
            if encoding:
                return content_bytes.decode(encoding)
            else:
                return content_bytes # Return bytes if no encoding specified
        except oss2.exceptions.NoSuchKey:
            print(f"Error: Object not found in OSS: {object_key}")
            return None
        except Exception as e:
            print(f"Error reading OSS object {object_key}: {e}")
            return None

    def iterate_object_at(self, prefix):
        return oss2.ObjectIterator(self.bucket, prefix = prefix)


class CredentialProviderWarpper(CredentialsProvider):
    def __init__(self, client):
        self.client = client

    def get_credentials(self):
        access_key_id = self.client.get_access_key_id()
        access_key_secret = self.client.get_access_key_secret()
        security_token = self.client.get_security_token()
        return Credentials(access_key_id, access_key_secret, security_token)


def initialize():
    role_name = os.getenv('RAM_ROLE_NAME') 
    bucket_name = os.getenv('BUCKET_NAME')  
    endpoint = os.getenv('BUCKET_ENDPOINT')
    config = Config(
        type='ecs_ram_role',      # 访问凭证类型。固定为ecs_ram_role。
        role_name=role_name
    )
    cred = Client(config)
    credentials_provider = CredentialProviderWarpper(cred)
    auth = oss2.ProviderAuth(credentials_provider)

    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    return OssBucket(bucket)
