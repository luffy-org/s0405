from django import forms
from django.core.exceptions import ValidationError
from qcloud_cos.cos_exception import CosServiceError

from utils.Tencent.Cos import head_object
from web.forms.bootstrap import BootStrapForm
from web.models import PorjectFile


class FolderModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = PorjectFile
        fields = ['title']

    def __init__(self, request, parent_obj, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_obj = parent_obj

    def clean_title(self):
        file_name = self.cleaned_data.get('title')
        query = PorjectFile.objects.filter(project=self.request.tracer.project, title=file_name, file_type=1)
        if self.parent_obj:
            exists = query.filter(parent=self.parent_obj).exists()
        else:
            exists = query.filter(parent__isnull=True).exists()
        if exists:
            raise ValidationError('文件夹已存在')
        return file_name


class FileModelForm(BootStrapForm, forms.ModelForm):
    """
    前端完成上传文件后，将文件写入数据库
    """
    ETag = forms.CharField(max_length=64, label='ETag内容')

    class Meta:
        model = PorjectFile
        exclude = ['project', 'file_type', 'update_user', 'update_datetime']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request



    def clean_file_path(self):
        """
        对url进行拼接后存入数据库
        :return: 拼接后的URL
        """
        url = self.cleaned_data['file_path']
        return "https://{}".format(url)

    def clean(self):
        """
        调用cos接头获取到文件信息，与前端传递过来的信息进行对比，在写入数据库前再次进行校验，防止恶意写入数据库操作
        :return:
        """
        etag = self.cleaned_data['ETag']
        key = self.cleaned_data['key']
        size = self.cleaned_data['file_capacity']

        # 调用cos接口
        try:
            response = head_object(self.request.tracer.project.bucket, key)
        except CosServiceError as e:
            # 如果查询不到对象，说明提供的参数不对，直接返回clean_data
            return self.cleaned_data
        ret_etag = response['ETag']
        ret_size = int(response['Content-Length'])

        if etag != ret_etag:
            self.add_error('etag', 'ETag错误')

        if size != ret_size:
            self.add_error('file_capacity', '文件大小不一致')

        return self.cleaned_data
