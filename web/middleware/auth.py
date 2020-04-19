from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from s0405 import settings
from web.models import UserInfo


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_id = request.session.get('user_id', 0)
        user_obj = UserInfo.objects.filter(pk=user_id).first()

        print('查看user_obj', user_obj)
        print('查看路径', request.path_info)
        request.user = user_obj
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return  # 直接return程序会继续往下执行
        if not user_obj:
            return redirect('/login/')


