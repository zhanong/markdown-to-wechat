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

class OssBucket:
  def __init__(self, bucket):
    self.bucket = bucket

  def get_object_to_file(self, object_key, local_file)
    self.bucket.get_object_to_file(object_key, local_file)


class CredentialProviderWarpper(CredentialsProvider):
    def __init__(self, client):
        self.client = client

    def get_credentials(self):
        access_key_id = self.client.get_access_key_id()
        access_key_secret = self.client.get_access_key_secret()
        security_token = self.client.get_security_token()
        return Credentials(access_key_id, access_key_secret, security_token)


def initialze_Bucket(bucket_name, endpoint, object_key, local_file, role_name):
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
