import datetime
import json
import os

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_redis import get_redis_connection
from s0405 import settings
from utils.alipay import AliPay
from utils.encrypt import uid
from web import models
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import decodebytes, encodebytes
from urllib.parse import quote_plus


def index(request):
    return render(request, 'index.html')


def price(request):
    """付款页面"""
    price_policy_list = models.PricePolicy.objects.filter(category=2)

    return render(request, 'price.html', {'policy_list': price_policy_list})


def payment(request, policy_id):
    """订单页面"""

    policy_object = models.PricePolicy.objects.filter(id=policy_id, category=2).first()
    if not policy_object:
        return redirect('price')
    # 2. 拿到用户提交的购买数量
    number = request.GET.get('number', '')
    if not number or not number.isdecimal():
        return redirect('price')
    number = int(number)

    # 3. 计算购买价格
    origin_price = number * policy_object.price

    # 4. 之前买过套餐的进行抵扣
    balance = 0
    _object = None
    # 4.1 判断一下之前是否是付费套餐
    if request.tracer.price_policy.category == 2:
        # 4.2 找到该用户的最新一条交易记录
        _object = models.OrderRecord.objects.filter(status=1, user=request.tracer.user).order_by('-id').first()

        # total_timedelta:该交易记录购买套餐时间，既默认购买一个套餐是一年。
        total_timedelta = _object.end_time - _object.start_time

        # balance_timedelta: 套餐有效期还剩多少天
        balance_timedelta = _object.end_time - datetime.datetime.now()

        if total_timedelta.days == balance_timedelta.days:
            # 购买套餐后马上又买其他套餐的情况
            balance = _object.price.price * _object.count / total_timedelta * (balance_timedelta.days - 1)
        else:
            balance = _object.price.price * _object.count / total_timedelta * balance_timedelta.days

    if balance >= origin_price:
        return redirect('price')

    context = {
        'policy_id': policy_object.id,
        'number': number,
        'origin_prioce': origin_price,
        'balance': round(balance, 2),
        'total_price': origin_price - round(balance, 2)
    }
    conn = get_redis_connection()
    key = 'payment_{}'.format(request.tracer.user.mobile_phone)
    conn.set(key, json.dumps(context), ex=60 * 30)
    context['policy_object'] = policy_object
    context['transaction'] = _object

    return render(request, 'payment.html', context)



def pay(request):
    """创建支付接口"""

    conn = get_redis_connection()
    key = 'payment_{}'.format(request.tracer.user.mobile_phone)
    context_string = conn.get(key)
    if not context_string:
        return redirect('price')
    context = json.loads(context_string.decode('utf-8'))
    order_id = uid(request.tracer.user.mobile_phone)
    total_amount = context['total_price']

    # 1. 创建一个订单，未支付状态
    models.OrderRecord.objects.create(
        status=0,
        order=order_id,
        user=request.tracer.user,
        price_id=context['policy_id'],
        count=context['number'],
        actual_payment=total_amount
    )

    # 2. 根据订单信息+支付宝接口  == 支付链接
    params = {
        'app_id': '沙箱环境app_id',
        'method': 'alipay.trade.page.pay',
        'format': 'JSON',
        'charset': 'utf-8',
        'sign_type': 'RSA2',
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'version': '1.0',
        'biz_content': json.dumps({
            'out_trade_no': order_id,
            'product_code': 'FAST_INSTANT_TRADE_PAY',
            'total_amount': total_amount,
            'subject': '购买套餐'
        }, separators=(',', ':'))
    }


    # 2.1 排序+转换格式 == 待加密的字符串
    # unsigned_string 待签名字符串
    unsigned_string = '&'.join(["{}={}".format(key, params[key])  for key in sorted(params)])

    # 2.2 拿到自己的自己的应用私钥
    private_key = RSA.importKey(open(os.path.join(settings.BASE_DIR, 'files/应用私钥2048.txt')).read())

    # 2.3 结合私钥进行加密啊
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(SHA256.new(unsigned_string.encode('utf-8')))

    # 2.4 完成签名后进行base64编码

    sign_stgring = encodebytes(signature).decode('utf8').replace('\n', '')


    # 3 生成的sign值放回到字典中
    result = '&'.join(['{}={}'.format(k, quote_plus(params[k])) for k in sorted(params)])
    result = result + '&sign='+ quote_plus(sign_stgring)


    geteway = 'https://openapi.alipaydev.com/gateway.do'
    ali_pay_url = '{}?{}'.format(geteway, result)



    return redirect(ali_pay_url)

"""
def pay(request):
    params = {
        "app_id": "2016101900723416",
        "method": "alipay.trade.page.pay",
        "charset": "utf-8",
        "sign_type": "RSA2",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "1.0",
        "biz_content": json.dumps({
            "out_trade_no": "1592804974984",
            "product_code": "FAST_INSTANT_TRADE_PAY",
            "total_amount": 1999,
            "subject": "trace payment111"
        }, separators=(',', ':'))
    }
    unsigned_string = "&".join(["{0}={1}".format(k, params[k]) for k in sorted(params)])

    private_key = RSA.importKey(open(os.path.join(settings.BASE_DIR, 'files/应用私钥2048.txt')).read())
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(SHA256.new(unsigned_string.encode('utf-8')))
    sign_string = encodebytes(signature).decode("utf8").replace('\n', '')
    result = "&".join(["{0}={1}".format(k, quote_plus(params[k])) for k in sorted(params)])
    result = result + "&sign=" + quote_plus(sign_string)
    gateway = "https://openapi.alipaydev.com/gateway.do"

    ali_pay_url = "{}?{}".format(gateway, result)
    print(ali_pay_url)


"""