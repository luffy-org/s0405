
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.SettleDetailInfo import SettleDetailInfo
from alipay.aop.api.domain.SettleInfo import SettleInfo
from alipay.aop.api.domain.SubMerchant import SubMerchant
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest


if __name__ == '__main__':
    alipay_client_config = AlipayClientConfig()
    alipay_client_config.server_url = 'https://openapi.alipaydev.com/gateway.do'
    alipay_client_config.app_id = '[2016101900723416]'
    alipay_client_config.app_private_key = '[MIIEowIBAAKCAQEAj2OrrZVm8yqaRjMNzud4Td6w9F8OaWHWWBfp28CTcX7Sga6YRXF5fbeN1k0IjmffwYsg9nRv7ELQ9vcMjO2XWx6wtNG6Qe67HqIWDXQziWlK02+DmDX9qHP8Z2fTPaLb8iYJCSQ/Tc0DZv4i7yXzOIPEX5zsNZAGD52yJI3WW/l+58wUNV5uL2dhdx2d2HLy/Dc5FtAgj5IeKlgr8Dppw7exiIqbZzMGnU2xP65hxJISgK0Ilbjcd12d6OcD+mkJNVOnUBaapEJ8ewYrl+yZ1T+mqN3ovld8iKnc2gCGS4D/4aUD4MwlAOXp3XIAsLrwMcLl5fU/KzMWstFk2LooUQIDAQABAoIBACcjLVjTzqXQmwtOJBa1V0Dp56LLz0M0USz6WfqBNb1kwFBlN2q87kxCLZSwsgUslQZe00Bxx5rVIfRGukY9E3LrjY/NLumQH8LcuugxL1/yPVo4tdJ16iZwghQ3YpEQQrh1aUH1gtHZg3Q5KY/c6+YhERiH3HFCPmVExbr0e+3eYZrIxEFtadAkUOyYxY/CarHt368HqffNFTWdDBqJR0sBMG6sVjux9bFzYe5uRD8G5Tml/lhWxRBG8C9Lh8XYcQWHavROD6cbQm5BCkxtGw2KtVp8IW+IEkl8ts9Eizufcj/TJgqkU4MARmMLACYOS63jWJgNSBO02MLrOeqBcYECgYEA4kR57xBEdr5dxCxBzFrOvlyZsghYilq5jdHpWR3K1TYenln3fp9BI3eTeJsa1Pkb8y4pqR08CYZp00khja/wYI6eHg3iVQoBWmmwJjCgADz9BZ1TtGhtIoafYEkwr757TXb6w5JxzfUbfzlk8T9nj2A6e4JdWMAOOHijhuAxklsCgYEAojs3I6AKPCuu7EcOZF/CgqTCXszfpN5rYg2GJ6pJixqHR57SPaOmEy8295Yl1IEcwlk41wWx/A6MSSk4ibwK4QJo0iK0cbjIGFB8I2+qX/fkP2zV04n8pNy7QVE4yi78zBKoyxmJ/o4Gu6cCBgoT7QJR01PwSN2tnrBGpGosl8MCgYBLqI4FLDFYa0s7P3k49dxPtvMFntjMWo3VKC2YyOd7577RQFALnQDQ9TjwiRytviZkaDkx/T6ICNP1/GwlzoDYKJgigI3/1XqiWti1zGiT69DHQdYtawWjF9TPA2ouOclNG825+4vmTGFHZ0+jg4oDXS/xAKRp+r5Gj8BOZ0TsJQKBgAzOKcMJHeWz+QGzdiJcIKlZQfJjr39/AvDhamZ1HYr6VBVGJwgwg6pd/rO6SVAlxNReYIswauUfbNlVhJ3yltU98HItxRp44Gpy5+mQJd2fXofXGmWxLZ0Bw1IbjCUBYnjlPCeT432RTly/iPxbDUmW9kh9BqlpvguZlGnj65MrAoGBALACZ1nyw3bcy+D83OtmInaUkDhpb5cE9SX8jQ9/MV2MmkUmPTYdRL2C9GSGohIiXcLBqMW9UecrTM9sPaMh5+iGKXKyaqUTD9nCBL98IqxDclQEdnYg6C3aSYGyKv6z1/bYmtAHxpq1bi81zamTMlC99d0k0R5PO6zy8NL1x8py\
    ]'
    alipay_client_config.alipay_public_key = '[MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAhDIaTOUofHlDufdIXrWacJSAFZz7gHqNJL6b+Qh0wP26b4pP/+gTtETBFIR8JfM691UWtZuFGKVhu2tj2gkhgw/hhvmd6GCWFipahN8h6pJBFmKb0fdvTc314+lHtIm6JBylfJJ7XQULwTQkh9rCdwef+kouCjIFWUu+jpf0r3UeEt+4oSOal1Nj0NhkiNkeVi1jncRvMiMTxUE/ccezKnANMnTod5WGZlX5k3p1hdbt7bgpVpfF9FkHuZMwOqVQq/C7KWlDGYOCZL0EXbKbVYdR4eYeCZt4kCPOm37cUJ5SU/yWlqAXP3b3Vsjzrjv5E9BYuFd1AQRXA2QfY2xiFQIDAQAB]'

    client = DefaultAlipayClient(alipay_client_config=alipay_client_config)

    model = AlipayTradePagePayModel()
    model.out_trade_no = "pay201805020000226"  # 订单号
    model.total_amount = 500
    model.subject = "测试"
    model.product_code = "FAST_INSTANT_TRADE_PAY"
    settle_detail_info = SettleDetailInfo()
    settle_detail_info.amount = 50
    settle_detail_info.trans_in_type = "userId"
    settle_detail_info.trans_in = "2088302300165604"
    settle_detail_infos = list()
    settle_detail_infos.append(settle_detail_info)
    settle_info = SettleInfo()
    settle_info.settle_detail_infos = settle_detail_infos
    model.settle_info = settle_info
    sub_merchant = SubMerchant()
    sub_merchant.merchant_id = "2088301300153242"
    model.sub_merchant = sub_merchant
    request = AlipayTradePagePayRequest(biz_model=model)
    response = client.page_execute(request, http_method="GET")
    print("统一接口结果" + response)