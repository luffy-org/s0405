from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

secret_id = ''  # 替换为用户的 secretId
secret_key = ''  # 替换为用户的 secretKey
region = 'ap-guangzhou'  # 替换为用户的 Region
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)

# 2. 获取客户端对象
client = CosS3Client(config)


# 创建存储桶

response = client.create_bucket(
    Bucket='test1-1300310288',
    ACL='public-read'  # 权限： 私有写，公有读  默认为：读写私有
)


# 上传文件
response1 = client.upload_file(
    Bucket='test1-1300310288',
    LocalFilePath='./index-1.png',
    Key='myname.png'
)
print(response1['ETag'])
