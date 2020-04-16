from s0405 import settings
from django_redis import get_redis_connection
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20190711 import sms_client, models

def tencent_send_msg(phone, ret_num, template_id):
    try:
        cred = credential.Credential(settings.SecretId, settings.SecretKey)
        client = sms_client.SmsClient(cred, "ap-guangzhou")
        req = models.SendSmsRequest()
        req.SmsSdkAppid = settings.SmsSdkAppid
        req.Sign = settings.Sign
        req.ExtendCode = ""
        req.SenderId = ""
        req.PhoneNumberSet = ["+86%s" % phone]
        req.TemplateID = template_id
        req.TemplateParamSet = [ret_num]
        resp = client.SendSms(req)


    except TencentCloudSDKException as err:
        print(err)