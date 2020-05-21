from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from s0405 import settings



def delete_object(bucket, key, region='ap-guangzhou'):
    config = CosConfig(Region=region, SecretId=settings.SecretId, SecretKey=settings.SecretKey)
    client = CosS3Client(config)

    response = client.delete_object(
        Bucket=bucket,
        Key=key
    )
    return response


def delete_object_list(bucket, delete_list, region='ap-guangzhou'):
    config = CosConfig(Region=region, SecretId=settings.SecretId, SecretKey=settings.SecretKey)
    client = CosS3Client(config)
    response = client.delete_objects(
        Bucket=bucket,
        Delete={
            'Object': delete_list
        }
    )
    return response

del_list = [{'Key': 'exampleobject'}, {'Key': 'baf6c6f188f757d64deb489cf9e3e8e2.png'}]

ret = delete_object_list('18689763500-1300310288', del_list)
print(ret)