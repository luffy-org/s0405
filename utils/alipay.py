from datetime import datetime

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from base64 import decodebytes, encodebytes
import json


class AliPay:
    """支付宝支付接口"""

    def __init__(self, appid, app_notify_url, app_private_key_path, return_url):
        """
        :param appid: appID
        :param app_notify_url: 完成支付后支付宝向该地址发送post请求
        :param app_private_key_path: 私钥文件路径
        :param alipay_public_key_path: 支付宝公钥地址
        :param return_url: 完成支付后跳转地址
        """
        self.app_id = appid
        self.app_notify_uil = app_notify_url
        self.app_private_key_path = app_private_key_path
        self.app_private_key = None

        self.return_url = return_url
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())


    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        """请求参数"""
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }
        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, return_url)
        """
        
        data = {
        'app_id': '2016101900723416', 
        'method': 'alipay.trade.page.pay', 
        'charset': 'utf-8', 
        'sign_type': 'RSA2', 
        'timestamp': '2020-06-23 19:28:21',
        'version': '1.0', 
        'biz_content': {
            'subject': 'trace rpayment',
            'out_trade_no': 323904352, 
            'total_amount': 88, 
            'product_code': 'FAST_INSTANT_TRADE_PAY'
            }
        }

        """
        return self.sign_data(data)

    def build_body(self, method, biz_content, return_url=None):
        """
        公共参数
        :param method: api方法
        :param biz_content: 其他参数
        :param return_url: 支付成功后回跳地址
        :return:
        """
        data = {
            "app_id": self.app_id,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_uil
            data["return_url"] = return_url

        return data

    def sign_data(self, data):
        data.pop("sign", None)
        # 排序后的字符串
        # 排序后的列表
        unsigned_items = self.ordered_data(data)


        unsigned_string = '&'.join("{0}={1}".format(k, v) for k, v in unsigned_items)


        sign = self.sign(unsigned_string.encode('utf-8'))
        """
        sign = QCKwd+afnFqPVuFgSgj12f0VV4dRG4HZTWYk2XDT1utEYMuVmalIO22fLhj/ZXLJVnipG6KUDE3H/x8vq64SpZL7JjUaqqMY5hJwF9tFv/JENhWWrKyc+IIGd8i+mRhJezvHIrSj/S2N+pHPzjrKKPB9fk3UMe7Whjv1QL5+O1apI25zXrGZvgE6goPiOc12olqbPBmTSBE25G0Pz5rZMmxzODpDtf/xR8Y779W6owWOFMzgn+75QU+WwYL+Ggbg/Nu2pjs9ory4x/UbIA+uLURpTcZ+9/d0j5S41MsS9pz9GI86fFV9ZnKY8DTq0Lf5oy80M3dcPCzxrC9odibekw==
        """

        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        """
        app_id=2016101900723416&
        biz_content=%7B%22subject%22%3A%22trace+payment%22%2C%22out_trade_no%22%3A%22323904352%22%2C%22total_amount%22%3A88%2C%22product_code%22%3A%22FAST_INSTANT_TRADE_PAY%22%7D&charset=utf-8&
        method=alipay.trade.page.pay&
        sign_type=RSA2&
        timestamp=2020-06-23+19%3A58%3A33&
        version=1.0&
        sign=Qr3TMV0MeiRs%2Bq%2FUPnb9roRWs6M5tD8vziU1YISnqW6mz7GmjHFQmyG9LpOvF6r9mgnOv%2B9FlhJOj2NeEunplIqDYSrtv82%2BRI3XxRQDTleeSJbJNcM0GjT820%2FWP0gnJoZqpS05VnBKbQaGQ0GmsUpz7SqT5ar%2Fsi5f39ZQpnN%2BVcmBenwTj78LcR1%2BmZOnA%2BuZpAwSloTaVfAjG8CbOCobdRtY0EVc%2BIdGExfoOrNQfe%2FTOOTtqzo7gTMgEY%2FMapcxJ4yArjk9BE9yli5kLsnkAoWkykSUlZQlGIUNrO3RHK9M4Qh7Xhr%2FofwgoD4aHHQr1T4C%2BWbqg8wwxDggcg%3D%3D
        """
        return signed_string


    def ordered_data(self, data):
        """
        返回一个将value值是字典的进行序列化，并对整个data进行排序
        :param data:
        :return: [(key, value),(key, value)]
        """
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来

        for key in complex_keys:
            # 将data中value是字典的进行序列化，并去掉空格
            data[key] = json.dumps(data[key], separators=(',', ':'))

        """
        unsigned_items =
        [
            ('app_id', '2016101900723416'), 
            ('biz_content', '{"subject":"trace payment","out_trade_no":"323904352","total_amount":88,"product_code":"FAST_INSTANT_TRADE_PAY"}'), 
            ('charset', 'utf-8'), 
            ('method', 'alipay.trade.page.pay'), 
            ('sign_type', 'RSA2'), 
            ('timestamp', '2020-06-23 19:35:13'), 
            ('version', '1.0')
        ]
        """

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        """


        :param unsigned_string:
        'app_id=2016101900723416&
        biz_content={"subject":"trace payment","out_trade_no":"323904352","total_amount":88,"product_code":"FAST_INSTANT_TRADE_PAY"}&
        charset=utf-8&
        method=alipay.trade.page.pay&
        sign_type=RSA2&
        timestamp=2020-06-23 19:35:13&version=1.0'
        :return:
        """
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign
"""
    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)
"""