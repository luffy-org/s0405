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
    print('桶名称', bucket)
    config = CosConfig(Region=region, SecretId=settings.SecretId, SecretKey=settings.SecretKey)

    # 2. 获取客户端对象
    client = CosS3Client(config)

    # 3. 创建桶
    client.create_bucket(
        Bucket=bucket,
        ACL='public-read'  # 权限： 私有写，公有读  默认为：读写私有
    )

    # 4. 为桶设置跨域规则
    client.put_bucket_cors(
        Bucket=bucket,
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


def delete_object(bucket, key, region='ap-guangzhou'):
    """删除单个对象"""
    config = CosConfig(Region=region, SecretId=settings.SecretId, SecretKey=settings.SecretKey)
    client = CosS3Client(config)

    response = client.delete_object(
        Bucket=bucket,
        Key=key
    )
    return response


def delete_object_list(bucket, delete_list, region='ap-guangzhou'):
    """批量删除对象"""
    config = CosConfig(Region=region, SecretId=settings.SecretId, SecretKey=settings.SecretKey)
    client = CosS3Client(config)
    response = client.delete_objects(
        Bucket=bucket,
        Delete={
            'Object': delete_list
        }
    )
    return response
