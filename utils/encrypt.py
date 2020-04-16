import hashlib

from django.conf import settings


def md5(string):
    """
    进行md5加密
    :param string:
    :return:
    """
    hash_object = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))  # 加盐处理
    hash_object.update(string.encode('utf-8'))
    return hash_object.hexdigest()

