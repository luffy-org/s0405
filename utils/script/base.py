import sys
import os

import django

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(base_dir)
sys.path.append(base_dir)
# print(sys.path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 's0405.settings')
django.setup()