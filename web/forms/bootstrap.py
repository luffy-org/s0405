class BootStrapForm:
    bootstrap_class_exclude = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.bootstrap_class_exclude:
                continue
            old_class = field.widget.attrs.get('class', '')  # 获取在插件里设置里类名
            field.widget.attrs['class'] = '{} form-control'.format(old_class)
            field.widget.attrs['placeholder'] = '请输入%s' % field.label