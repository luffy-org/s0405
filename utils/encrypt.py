import hashlib
import uuid
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


def uid(ret_str):
    data = "{}-{}".format(str(uuid.uuid4()), ret_str)
    return md5(data)