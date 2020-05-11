from django.forms.widgets import RadioSelect


class ColorRadioSelect(RadioSelect):
    # template_name = 'django/forms/widgets/radio.html'
    # option_template_name = 'django/forms/widgets/radio_option.html'
    template_name = 'widgets/color_radio.html'
    option_template_name = 'widgets/color_radio_option.html'
