from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from s0405 import settings

region='ap-guangzhou'

config = CosConfig(Region=region, SecretId=settings.SecretId, SecretKey=settings.SecretKey)

# 2. 获取客户端对象
client = CosS3Client(config)


# 创建存储桶

response = client.create_bucket(
    Bucket='test1-1300310288',
    ACL='public-read'  # 权限： 私有写，公有读  默认为：读写私有
)

client.put_bucket_cors(
        Bucket='test1-1300310288',
        CORSConfiguration={
            'CORSRule': [
                {
                    'AllowedOrigin': '*',
                    'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
                    'AllowedHeader': '*',
                    'ExposeHeader': 'Etag',
                    'MaxAgeSeconds': 600
                }
            ]
        }
    )
# # 上传文件
# response1 = client.upload_file(
#     Bucket='test1-1300310288',
#     LocalFilePath='./index-1.png',
#     Key='myname.png'
# )
# print(response1['ETag'])
