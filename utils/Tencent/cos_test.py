from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from s0405 import settings


# def delete_object(bucket, key, region='ap-guangzhou'):
#     config = CosConfig(Region=region, SecretId=settings.SecretId, SecretKey=settings.SecretKey)
#     client = CosS3Client(config)
#
#     response = client.delete_object(
#         Bucket=bucket,
#         Key=key
#     )
#     return response
#
#
# def delete_object_list(bucket, delete_list, region='ap-guangzhou'):
#     config = CosConfig(Region=region, SecretId=settings.SecretId, SecretKey=settings.SecretKey)
#     client = CosS3Client(config)
#     response = client.delete_objects(
#         Bucket=bucket,
#         Delete={
#             'Object': delete_list
#         }
#     )
#     return response
#
# del_list = [{'Key': 'exampleobject'}, {'Key': 'baf6c6f188f757d64deb489cf9e3e8e2.png'}]
#
# ret = delete_object_list('18689763500-1300310288', del_list)
# print(ret)


def delete(bucket, region='ap-guangzhou'):
    config = CosConfig(Region=region, SecretId=settings.SecretId, SecretKey=settings.SecretKey)
    client = CosS3Client(config)
    while True:
        response_dict = client.list_objects(Bucket=bucket)  # 得到的结果中Contents才是查询数据
        print('查询到结果', response_dict)
        contents = response_dict.get('Contents', '')  # 储存桶为空的情况下获取不到Contents
        if not contents:
            break
        # 制作删除api需要的数据结构
        object_list = [{'Key': content['key']} for content in contents]
        object_dict = {'Object': object_list, 'Quiet': 'true'}
        # 删除查询到的数据
        client.delete_objects(Bucket=bucket, Delete=object_dict)
        if response_dict['IsTruncated'] == 'false':  # 如果没有被截断 退出循环
            break


def test(bucket, region='ap-guangzhou'):
    config = CosConfig(Region=region, SecretId=settings.SecretId, SecretKey=settings.SecretKey)
    client = CosS3Client(config)
    while True:
        multipart_dict = client.list_multipart_uploads(Bucket=bucket)
        print('查询碎片', multipart_dict)
        uploads = multipart_dict.get('Upload', '')
        if not uploads:
            break

        for upload in uploads:
            # 删除碎片
            client.abort_multipart_upload(Bucket=bucket, Key=upload['Key'], UploadId=upload['UploadId'])
        if multipart_dict['IsTruncated'] == 'false':
            break


delete('18689763500-1300310288')
