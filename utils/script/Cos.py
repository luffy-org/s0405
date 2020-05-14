from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from s0405 import settings


def create_bucket(bucket, region='ap-guangzhou'):
    """
    创建储存桶
    :param bucket:  储存桶名称
    :param region:  储存桶地区
    :return:
    """
    config = CosConfig(Region=region, SecretId=settings.SecretId, SecretKey=settings.SecretKey)

    # 2. 获取客户端对象
    client = CosS3Client(config)

    response = client.create_bucket(
        Bucket=bucket,
        ACL='public-read'  # 权限： 私有写，公有读  默认为：读写私有
    )


def upload_file(bucket, region, key, obj):
    """
    上传文件
    :param bucket:  存储桶名称
    :param region:  存储桶地区
    :param key:     文件加密后的名称和格式
    :param obj:     上传文件对象
    :return:
    """
    config = CosConfig(Region=region, SecretId=settings.SecretId, SecretKey=settings.SecretKey)

    # 2. 获取客户端对象
    client = CosS3Client(config)
    client.upload_file_from_buffer(
        Bucket=bucket,
        Key=key,
        Body=obj,
    )
    return 'https://{}.cos.{}.myqcloud.com/{}'.format(bucket, region, key)