from django_redis import get_redis_connection
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20190711 import sms_client, models

def tencent_send_msg(phone, ret_num):
    try:
        cred = credential.Credential('AKIDLPDk4aQrb6KMxt5u0tVqSnrd8MWggAVD', 'b5KJ6eiW280dgW68vRjV1IRJxY2FC6k8')
        client = sms_client.SmsClient(cred, "ap-guangzhou")
        req = models.SendSmsRequest()
        req.SmsSdkAppid = "1400349049"
        req.Sign = "Codeheng"
        req.ExtendCode = ""
        req.SenderId = ""
        req.PhoneNumberSet = ["+86%s" % phone]
        req.TemplateID = "577068"
        req.TemplateParamSet = [ret_num]
        resp = client.SendSms(req)
        # print('短信', resp.to_json_string(indent=2))
        # conn = get_redis_connection("default")
        # conn.set(phone, ret_num, ex=30)

    except TencentCloudSDKException as err:
        print(err)